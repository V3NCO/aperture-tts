const express = require('express');
const path = require('path');
const puppeteer = require('puppeteer');
const { join } = require('path');
const fs = require('fs');

const {MeetingSessionConfiguration, DefaultDeviceController, DefaultMeetingSession, ConsoleLogger, LogLevel, AudioProfile } = require('amazon-chime-sdk-js')
const serverApp = express();
serverApp.use(express.json());
const port = 7171;

let browser;     // shared browser instance
let page

async function getBrowser() {
  if (!browser) {
    browser = await puppeteer.launch({
      headless: true,
      protocolTimeout: 90000, // Increase protocol timeout to 90 seconds
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

serverApp.get('/', (req, res) => {
  res.send(`
    <html>
      <head>
        <title>Huddle Bot Client</title>
      </head>
      <body>
        <h1>Huddle Bot Client</h1>
      </body>
    </html>
  `);
});

serverApp.get('/amazon-chime-sdk.min.js', (req, res) => {
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
});

// thanks deployor for doing all the hard work before me :pf:
serverApp.post('/join', async (req, res) => {
  try {
    const { meeting, attendee } = req.body;
    if (!meeting || !attendee) {
      return res.status(400).json({ ok: false, error: 'Missing meeting or attendee object or wtvr' })
    };

    const browser = await getBrowser();
    page = await browser.newPage();
    page.setDefaultTimeout(90000); // 90 seconds page timeout

    // Log console messages from the browser page to the Node console
    page.on('console', msg => console.log('PAGE LOG:', msg.text()));
    page.on('error', err => console.error('PAGE ERROR', err));
    page.on('pageerror', e => console.error('PAGEERROR', e));

    await page.goto(`http://localhost:${port}/`);
    await page.addScriptTag({ path: join(__dirname, 'amazon-chime-sdk.min.js') });
    await page.waitForFunction(() => typeof window.ChimeSDK !== 'undefined', { timeout: 10000 });
      await page.evaluate(({ m, a }) => {
        window.meeting = m;
        window.attendee = a;
      }, { m: req.body.meeting, a: req.body.attendee });

    page.evaluate(async () => {
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
      // Microphone source
      window.audioSource = window.audioContext.createMediaStreamSource(mediaStream);
      window.gainNode = window.audioContext.createGain();
      window.gainNode.gain.value = 0; // Start muted
      window.audioSource.connect(window.gainNode);
      window.gainNode.connect(window.audioDestination);

      // Playback source (for TTS)
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
          // You might want to trigger a restart or cleanup here.
        }
      });
    });

    res.json({ ok: true, message: 'Successfully joined meeting' })
  } catch (err) {
    console.error('Error joining chime meeting: ', err);
    res.status(500).json({ ok: false, error: 'Failed to join meeting: '+err.message });
  }
});

serverApp.post('/play-audio', express.raw({ type: 'audio/wav', limit: '1000mb' }), async (req, res) => {
  try {
    if (!page) {
      return res.status(400).json({
        ok: false,
        error: 'No active meeting page. Call /join first.',
      });
    }

    const wavBuffer = req.body;
    if (!Buffer.isBuffer(wavBuffer) || wavBuffer.length === 0) {
      return res.status(400).json({
        ok: false,
        error: 'Invalid audio data',
      });
    }

    const base64 = wavBuffer.toString('base64');
    const dataUrl = `data:audio/wav;base64,${base64}`;

    await page.evaluate(async (url) => {
      if (!window.PlaybackElement) {
        console.error('PlaybackElement not found. Was the /join setup successful?');
        return;
      }

      window.PlaybackElement.src = url;
      try {
        await window.PlaybackElement.play();
        console.log('Playback started.');
      } catch (e) {
        console.error('Error playing audio in browser:', e);
      }
    }, dataUrl);

    res.json({ ok: true, message: 'Audio playback triggered' });
    } catch (err) {
      console.error('Error playing audio: ', err);
      res
        .status(500)
        .json({ ok: false, error: 'Failed to play audio: ' + err.message });
    }
  }
);

serverApp.post('/leave', async (req, res) => {
  try {
    if (!page) {
      return res.status(400).json({
        ok: false,
        error: 'No active meeting page to leave.',
      });
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
    page = null; // Reset the page variable

    res.json({ ok: true, message: 'Successfully left the meeting.' });
  } catch (err) {
    console.error('Error leaving meeting: ', err);
    res.status(500).json({ ok: false, error: 'Failed to leave meeting: ' + err.message });
  }
})

serverApp.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
