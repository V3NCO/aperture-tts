const readline = require('readline');
const puppeteer = require('puppeteer');
const { join } = require('path');
const path = require('path');
const fs = require('fs');
const http = require('http');

const {MeetingSessionConfiguration, DefaultDeviceController, DefaultMeetingSession, ConsoleLogger, LogLevel, AudioProfile } = require('amazon-chime-sdk-js')

let browser;
let page;
const port = 7171;

const server = http.createServer((req, res) => {
  if (req.url === '/') {
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(`<html><head><title>Huddle Bot Client</title></head><body><h1>Huddle Bot Client</h1></body></html>`);
  } else if (req.url === '/amazon-chime-sdk.min.js') {
    const sdkPath = path.join(__dirname, 'amazon-chime-sdk.min.js');
    fs.readFile(sdkPath, (err, data) => {
      if (err) {
        res.writeHead(404);
        res.end('Not found');
        return;
      }
      res.writeHead(200, { 'Content-Type': 'application/javascript' });
      res.end(data);
    });
  } else {
    res.writeHead(404);
    res.end('Not found');
  }
});

server.listen(port);

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false
});

async function handleRpcRequest(request) {
  const { id, method, params } = request;

  try {
    let result;

    switch (method) {
      case 'join':
        result = await rpcJoin(params);
        break;
      case 'play_audio':
        result = await rpcPlayAudio(params);
        break;
      case 'leave':
        result = await rpcLeave(params);
        break;
      default:
        throw new Error(`Unknown method: ${method}`);
    }

    const response = { id, result };
    console.log(JSON.stringify(response));
  } catch (error) {
    const response = { id, error: error.message };
    console.log(JSON.stringify(response));
  }
}

rl.on('line', async (line) => {
  try {
    const request = JSON.parse(line);
    await handleRpcRequest(request);
  } catch (error) {
    console.error('Error processing RPC request:', error);
  }
});

async function getBrowser() {
  if (!browser) {
    browser = await puppeteer.launch({
      headless: true,
      protocolTimeout: 90000, // Increase protocol timeout to 90 seconds; DO NOT REMOVE
      args: [
            '--no-sandbox',
            '--disable-web-security',
            '--autoplay-policy=no-user-gesture-required',
            '--disable-gpu',
            '--disable-dev-shm-usage',
            '--single-process',
            '--no-zygote',
            '--disable-infobars',
            '--no-default-browser-check',
            '--no-first-run',
            '--use-fake-ui-for-media-stream',
            '--use-fake-device-for-media-stream'
          ],
    });
  }
  return browser;
}

async function rpcJoin(params) {
  const { meeting, attendee } = params;

  if (!meeting || !attendee) {
    throw new Error('Missing meeting or attendee object');
  }

  const browser = await getBrowser();
  page = await browser.newPage();
  page.setDefaultTimeout(90000);

  page.on('console', msg => console.error('PAGE LOG:', msg.text()));
  page.on('error', err => console.error('PAGE ERROR', err));
  page.on('pageerror', e => console.error('PAGEERROR', e));

  await page.goto(`http://localhost:${port}/`);
  await page.addScriptTag({ path: join(__dirname, 'amazon-chime-sdk.min.js') });
  await page.waitForFunction(() => typeof window.ChimeSDK !== 'undefined', { timeout: 10000 });

  await page.evaluate(({ m, a }) => {
    window.meeting = m;
    window.attendee = a;
  }, { m: meeting, a: attendee });

  await page.evaluate(async () => {
    console.log('1. Setting up Chime session objects...');
    const { MeetingSessionConfiguration, DefaultDeviceController, DefaultMeetingSession, ConsoleLogger, LogLevel, AudioProfile } = window.ChimeSDK;
    const logger = new ConsoleLogger('Logger', LogLevel.INFO);
    const deviceController = new DefaultDeviceController(logger, { enableWebAudio: true });
    const config = new MeetingSessionConfiguration(window.meeting, window.attendee);
    config.audioProfile = AudioProfile.fullbandMusicStereo();
    window.meetingSession = new DefaultMeetingSession(config, logger, deviceController);

    console.log('2. Starting main audio/video session...');
    await window.meetingSession.audioVideo.start();
    console.log('   Main audio/video session started.');

    console.log('3. Setting up local audio graph (AudioContext)...');
    window.audioContext = new AudioContext();
    await window.audioContext.resume();
    window.audioDestination = window.audioContext.createMediaStreamDestination();
    console.log('   AudioContext is ready.');

    console.log('4. Getting user media (mic)...');
    const mediaStream = await navigator.mediaDevices.getUserMedia({ audio: { noiseSuppression: false, echoCancellation: false, autoGainControl: false, sampleRate: 48000, channelCount: 2 } });
    console.log('   User media obtained.');

    console.log('5. Connecting media sources to audio graph...');
    window.audioSource = window.audioContext.createMediaStreamSource(mediaStream);
    window.gainNode = window.audioContext.createGain();
    window.gainNode.gain.value = 0;
    window.audioSource.connect(window.gainNode);
    window.gainNode.connect(window.audioDestination);

    window.PlaybackElement = new Audio();
    window.PlaybackElement.crossOrigin = 'anonymous';
    window.PlaybackElement.loop = false;
    const playbackSourceNode = window.audioContext.createMediaElementSource(window.PlaybackElement);
    window.PlaybackGain = window.audioContext.createGain();
    window.PlaybackGain.gain.value = 0.75;
    playbackSourceNode.connect(window.PlaybackGain);
    window.PlaybackGain.connect(window.audioDestination);
    console.log('   All audio sources connected.');

    console.log('7. Creating and starting content share stream...');
    const contentStream = window.audioDestination.stream;
    await window.meetingSession.audioVideo.startContentShare(contentStream);
    console.log('   Content share started successfully!');

    window.meetingSession.audioVideo.addObserver({
      audioVideoDidStop: (sessionStatus) => {
        console.log('Chime session stopped. Status:', sessionStatus.description());
      }
    });
  });

  return { ok: true, message: 'Successfully joined meeting' };
}

async function rpcPlayAudio(params) {
  const { audioBase64 } = params;

  if (!page) {
    throw new Error('No active meeting page. Call join first.');
  }

  if (!audioBase64) {
    throw new Error('Missing audioBase64 parameter');
  }

  const dataUrl = `data:audio/wav;base64,${audioBase64}`;

  await page.evaluate(async (url) => {
    if (!window.PlaybackElement) {
      throw new Error('PlaybackElement not found. Was the join setup successful?');
    }

    window.PlaybackElement.src = url;
    try {
      await window.PlaybackElement.play();
      console.log('Playback started.');
    } catch (e) {
      console.error('Error playing audio in browser:', e);
      throw e;
    }
  }, dataUrl);

  return { ok: true, message: 'Audio playback triggered' };
}

async function rpcLeave(params) {
  if (!page) {
    throw new Error('No active meeting page to leave.');
  }

  await page.evaluate(async () => {
    if (window.meetingSession) {
      console.log('Stopping content share...');
      await window.meetingSession.audioVideo.stopContentShare();
      console.log('Content share stopped.');

      console.log('Stopping audio/video session...');
      window.meetingSession.audioVideo.stop();
      console.log('Audio/video session stopped.');

      if (window.audioContext) {
        console.log('Closing AudioContext...');
        await window.audioContext.close();
        console.log('AudioContext closed.');
      }
    }
  });

  await page.close();
  page = null;

  return { ok: true, message: 'Successfully left the meeting.' };
}

process.on('SIGINT', async () => {
  if (page) {
    try {
      await rpcLeave({});
    } catch (error) {
      console.error('Error during shutdown:', error);
    }
  }
  process.exit(0);
});

process.on('SIGTERM', async () => {
  if (page) {
    try {
      await rpcLeave({});
    } catch (error) {
      console.error('Error during shutdown:', error);
    }
  }
  process.exit(0);
});
