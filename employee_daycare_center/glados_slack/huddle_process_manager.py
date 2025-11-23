import asyncio
from typing import Dict, Optional, Any
import json
from pathlib import Path


class HuddleProcessError(Exception):
    """Error when huddle fails"""
    pass
class HuddleProcess:
    """Manages Huddle.js subprocesses individually or wtvr"""

    def __init__(self, channel_id: str, huddle_js_path: str):
        self.channel_id = channel_id
        self.huddle_js_path = huddle_js_path
        self.process: Optional[asyncio.subprocess.Process] = None
        self.request_counter = 0
        self.pending_responses: Dict[int, asyncio.Future] = {}
        self.reader_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Launch the Huddle subprocess"""
        from glados_slack.env import logger

        if self.process is not None:
            logger.warning(f"{self.channel_id} is already running !")
            return

        try:
            self.process = await asyncio.create_subprocess_exec(
                "node", self.huddle_js_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            logger.info(f"Huddle {self.channel_id} started with PID  {self.process.pid}")

            self.reader_task = asyncio.create_task(self._read_responses())
        except Exception as e:
            logger.error(f"Failed to start huddle {self.channel_id}: {e}")
            raise HuddleProcessError(f"Failed to start process: {e}") # I should do clean errors more often it's satisfying but I'm too lazy :p

    async def _read_responses(self) -> None:
        """Background task that reads process stdout"""
        from glados_slack.env import logger

        try:
            while self.process is not None:
                if self.process.stdout is None:
                    break

                if self.process.stdout.at_eof():
                    break

                line = await self.process.stdout.readline()
                if not line:
                    break
                try:
                    response = json.loads(line.decode())
                    request_id = response.get("id")

                    if request_id is not None and request_id in self.pending_responses:
                        future = self.pending_responses.pop(request_id)
                        if not future.done():
                            future.set_result(response)
                    else:
                        logger.warning(f"unknonwn req id {request_id}: {response}")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON response: {e}, line: {line}")
                except Exception as e:
                    logger.error(f"Error processing response: {e}")

        except asyncio.CancelledError:
            logger.debug(f"reader task cancelled for {self.channel_id}")
        except Exception as e:
            logger.error(f"reader task error at {self.channel_id}: {e}")
        finally:
            logger.info(f"end of {self.channel_id}'s reader task")

    async def call(self, method: str, params: Optional[Dict[str, Any]] = None, timeout: float = 30) -> Any:
        """Call method in huddle.js subprocess"""

        if self.process is None:
            raise HuddleProcessError(f"Huddle process {self.channel_id} not running")

        self.request_counter += 1
        request_id = self.request_counter

        request = {
            "id": request_id,
            "method": method,
            "params": params or {}
        }

        try:
            response_future = asyncio.Future()
            self.pending_responses[request_id] = response_future

            if self.process.stdin is None:
                raise HuddleProcessError("Process stdin is not available")

            request_json = json.dumps(request) + "\n"
            self.process.stdin.write(request_json.encode())
            await self.process.stdin.drain()

            response = await asyncio.wait_for(response_future, timeout=timeout)
            if "error" in response:
                raise HuddleProcessError(f"Method '{method}' failed: {response['error']}")

            return response.get("result")
        except asyncio.TimeoutError:
            self.pending_responses.pop(request_id, None)
            raise HuddleProcessError(f'{method} TO after {timeout}s')
        except Exception as e:
            self.pending_responses.pop(request_id, None)
            raise HuddleProcessError(f"Call to '{method}' failed: {e}")

    async def terminate(self) -> None:
        """Kill the sub"""
        from glados_slack.env import logger

        if self.process is None:
            logger.warning(f"Process {self.channel_id} not running")
            return

        try:
            logger.info(f"terminating Huddle proc {self.channel_id}")

            if self.process.stdin:
                self.process.stdin.close()
                try:
                    await asyncio.wait_for(self.process.wait(), timeout=5)
                except asyncio.TimeoutError:
                    logger.warning(f"process {self.process.pid} didnt exit, killing it")
                    self.process.kill()
                    try:
                        await asyncio.wait_for(self.process.wait(), timeout=2.0)
                    except asyncio.TimeoutError:
                        logger.error(f"failed to kill process {self.process.pid}")

            if self.reader_task and not self.reader_task.done():
                self.reader_task.cancel()
                try:
                    await self.reader_task
                except asyncio.CancelledError:
                    pass
            self.process = None
            logger.info(f"Huddle proc {self.channel_id} term")
        except Exception as e:
            logger.error(f"Err term huddle proc {self.channel_id}: {e}")

class HuddleProcessManager:
    """Manage multiple huddle.js subproc (1/channel)"""

    def __init__(self, huddle_js_path: Optional[str] = None):
        from glados_slack.env import logger
        self.huddle_js_path = huddle_js_path or self._get_default_huddle_js_path()
        self.processes: Dict[str, HuddleProcess] = {}
        logger.info(f"Initialized HuddleProcessManager with Huddle.js at: {self.huddle_js_path}")

    @staticmethod
    def _get_default_huddle_js_path() -> str:
        """get path for huddle js"""
        current_dir = Path(__file__).parent
        huddle_js_path = current_dir / "callhandler" / "Huddle.js"
        if not huddle_js_path.exists():
            raise HuddleProcessError(f"Huddle.js not found at {huddle_js_path}")
        return str(huddle_js_path)

    async def get_or_create_huddle(self, channel_id: str) -> HuddleProcess:
        """get existing or create process for given channel"""
        if channel_id not in self.processes:
            huddle = HuddleProcess(channel_id, self.huddle_js_path)
            await huddle.start()
            self.processes[channel_id] = huddle
        return self.processes[channel_id]

    async def destroy_huddle(self, channel_id: str) -> None:
        """Destroy HuddleProcess : leave and clean"""
        from glados_slack.env import logger

        if channel_id in self.processes:
            huddle = self.processes[channel_id]
            try:
                # Try to gracefully leave the meeting first
                await huddle.call("leave", timeout=10.0)
            except HuddleProcessError as e:
                logger.warning(f"Failed to clean leave meeting {channel_id}: {e}")

            await huddle.terminate()
            del self.processes[channel_id]
        else:
            logger.warning(f"no huddle proc for {channel_id} twin")

    async def shutdown_all(self) -> None:
        """Shutdown all huddle processes."""
        from glados_slack.env import logger
        logger.info("Shutting down all Huddle processes")
        for channel_id in list(self.processes.keys()):
            await self.destroy_huddle(channel_id)
        logger.info("All Huddle processes shut down")

_manager: Optional[HuddleProcessManager] = None


def get_huddle_manager() -> HuddleProcessManager:
    """Get the global HuddleProcessManager instance."""
    global _manager
    if _manager is None:
        _manager = HuddleProcessManager()
    return _manager


async def get_or_create_huddle(channel_id: str) -> HuddleProcess:
    """Helper function to get or create a huddle for a channel."""
    return await get_huddle_manager().get_or_create_huddle(channel_id)


async def destroy_huddle(channel_id: str) -> None:
    """Helper function to destroy a huddle for a channel."""
    await get_huddle_manager().destroy_huddle(channel_id)
