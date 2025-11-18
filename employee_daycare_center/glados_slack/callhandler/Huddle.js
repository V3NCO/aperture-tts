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

    await page.goto(`http://localhost:${port}/`);
    await new Promise(resolve => setTimeout(resolve, 2000));
    await page.addScriptTag({ path: join(__dirname, 'amazon-chime-sdk.min.js') });
    await page.waitForFunction(() => typeof window.ChimeSDK !== 'undefined', { timeout: 10000 });
      await page.evaluate(({ m, a }) => {
        window.meeting = m;
        window.attendee = a;
      }, { m: req.body.meeting, a: req.body.attendee });
    await page.evaluate(async () => {
      const { MeetingSessionConfiguration, DefaultDeviceController, DefaultMeetingSession, ConsoleLogger, LogLevel, AudioProfile } = window.ChimeSDK;
      const logger = new ConsoleLogger('Logger', LogLevel.INFO);
      const deviceController = new DefaultDeviceController(logger, { enableWebAudio: true });
      const config = new MeetingSessionConfiguration(window.meeting, window.attendee);
      config.audioProfile = AudioProfile.fullbandMusicStereo();
      window.meetingSession = new DefaultMeetingSession(config, logger, deviceController);
      window.audioElement = document.createElement('audio');
      window.audioElement.autoplay = false;
      window.audioElement.muted = false;
      document.body.appendChild(window.audioElement);
      window.meetingSession.audioVideo.bindAudioElement(window.audioElement);
      window.deviceController = deviceController;
      window.isMuted = true;
      window.isStreamOn = true;
      window.showCamera = true;
      window.isAudioOutputEnabled = true;
      window.audioContext = new AudioContext();
      await window.audioContext.resume();
      window.audioDestination = window.audioContext.createMediaStreamDestination();
      await window.meetingSession.audioVideo.start();

      const devices = await navigator.mediaDevices.enumerateDevices();
          const audioDevices = devices.filter(device => device.kind === 'audioinput');
          const mediaStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: { noiseSuppression: false, echoCancellation: false, autoGainControl: false, sampleRate: 48000, channelCount: 2 } });
          const initialAudioTrack = mediaStream.getAudioTracks()[0];
          window.videoElement = document.createElement('video');
          window.videoElement.srcObject = mediaStream;
          await window.videoElement.play();
          const initialVideoTrack = mediaStream.getVideoTracks()[0];
          window.audioSource = window.audioContext.createMediaStreamSource(mediaStream);
          window.gainNode = window.audioContext.createGain();
          window.gainNode.gain.value = 0;
          window.audioSource.connect(window.gainNode);
          window.isConnected = initialVideoTrack.enabled && !initialVideoTrack.muted && initialVideoTrack.readyState === 'live';
          window.gainNode.connect(window.audioDestination);

          window.canvas = document.createElement('canvas');
          window.canvas.width = 1920;
          window.canvas.height = 1080;
          window.ctx = window.canvas.getContext('2d');

          window.timeCanvas = document.createElement('canvas');
          window.timeCanvas.width = window.canvas.width;
          window.timeCanvas.height = window.canvas.height;
          window.timeCtx = window.timeCanvas.getContext('2d');

          window.iconCanvas = document.createElement('canvas');
          window.iconCanvas.width = window.canvas.width;
          window.iconCanvas.height = window.canvas.height;
          window.iconCtx = window.iconCanvas.getContext('2d');

          // window.updateTime = () => {
          //   window.timeCtx.clearRect(0, 0, window.timeCanvas.width, window.timeCanvas.height);
          //   const now = new Date();
          //   const time24 = now.toLocaleTimeString('en-US', { hour12: false });
          //   const time12 = now.toLocaleTimeString('en-US', { hour12: true });
          //   window.timeCtx.fillStyle = 'white';
          //   window.timeCtx.font = '48px serif';
          //   window.timeCtx.fillText(`24h: ${time24}`, 50, 50);
          //   window.timeCtx.fillText(`12h: ${time12}`, 50, 100);
          // };

          // window.updateIcons = () => {
          //   window.iconCtx.clearRect(0, 0, window.iconCanvas.width, window.iconCanvas.height);
          //   const iconSize = 40;
          //   window.iconCtx.font = `900 ${iconSize}px "Font Awesome 6 Free"`;
          //   const rightX = window.canvas.width - 60;
          //   const iconYStart = 40;
          //   const iconSpacing = 50;
          //   let currentY = iconYStart;
          //   window.iconCtx.fillStyle = window.isMuted ? 'red' : 'green';
          //   window.iconCtx.fillText(window.isMuted ? '\uf131' : '\uf130', rightX, currentY);
          //   currentY += iconSpacing;
          //   window.iconCtx.fillStyle = (window.showCamera && window.isConnected) ? 'green' : 'red';
          //   window.iconCtx.fillText(window.showCamera ? '\uf03d' : '\uf4e2', rightX, currentY);
          //   currentY += iconSpacing;
          //   window.iconCtx.fillStyle = window.isAudioOutputEnabled ? 'green' : 'red';
          //   window.iconCtx.fillText(window.isAudioOutputEnabled ? '\uf028' : '\uf026', rightX, currentY);
          // };

          // window.updateTime();
          // window.updateIcons();
          // setInterval(window.updateTime, 1000);

          // window.fallbackImage = new Image();
          // window.fallbackImage.src = 'http://localhost:3001/oop.png';
          // window.fallbackImage.onload = () => {};
          window.isStreamOn = true;

          window.attemptRecovery = async function() {
            if (!window.showCamera) return;
            if (window.isConnected) return;
            try {
              const devicesRecovery = await navigator.mediaDevices.enumerateDevices();
              const audioDevicesRecovery = devicesRecovery.filter(device => device.kind === 'audioinput');
              const newStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: { noiseSuppression: false, echoCancellation: false, autoGainControl: false, sampleRate: 48000, channelCount: 2 } });
              if (window.audioSource) window.audioSource.disconnect();
              const audioTrackRecovery = newStream.getAudioTracks()[0];
              window.videoElement.srcObject = newStream;
              await window.videoElement.play();
              const recoveredTrack = newStream.getVideoTracks()[0];
              window.audioSource = window.audioContext.createMediaStreamSource(newStream);
              window.audioSource.connect(window.gainNode);
              window.gainNode.gain.value = window.isMuted ? 0 : 1;
              window.isConnected = recoveredTrack.enabled && !recoveredTrack.muted && recoveredTrack.readyState === 'live';

            } catch (err) {
              setTimeout(window.attemptRecovery, 5000);
            }
          };

          const videoTrack = mediaStream.getVideoTracks()[0];
          videoTrack.onended = () => {
            window.isConnected = false;
            if (window.showCamera) window.attemptRecovery();
          };
          videoTrack.onmute = () => {
            window.isConnected = false;
            if (window.showCamera) window.attemptRecovery();
          };

          let lastDrawTime = 0;
          const frameInterval = 1000 / 15;
      window.drawToCanvas = () => {
        const currentTime = performance.now();
        if (currentTime - lastDrawTime < frameInterval) {
          requestAnimationFrame(window.drawToCanvas);
          return;
        }
        lastDrawTime = currentTime;

        window.ctx.fillStyle = 'black';
        window.ctx.fillRect(0, 0, window.canvas.width, window.canvas.height);

        if (window.showCamera && window.isConnected) {
          window.ctx.drawImage(window.videoElement, 0, 0, window.canvas.width, window.canvas.height);
        } else {
          let text = window.showCamera ? 'woops connection lost to camera' : 'Video Turned Off';
          if (window.fallbackImage.complete) {
            const imgWidth = window.fallbackImage.width;
            const imgHeight = window.fallbackImage.height;
            const x = (window.canvas.width - imgWidth) / 2;
            const y = (window.canvas.height - imgHeight) / 2;
            window.ctx.drawImage(window.fallbackImage, x, y, imgWidth, imgHeight);
          }
          window.ctx.fillStyle = 'white';
          window.ctx.font = '48px serif';
          window.ctx.fillText(text, 50, 150);
        }

        window.ctx.drawImage(window.timeCanvas, 0, 0);
        window.ctx.drawImage(window.iconCanvas, 0, 0);

        requestAnimationFrame(window.drawToCanvas);
      }
      window.drawToCanvas();
      await window.attemptRecovery();

      const videoStream = window.canvas.captureStream(15);
      const contentAudioTrack = window.audioDestination.stream.getAudioTracks()[0];
      const contentStream = new MediaStream([videoStream.getVideoTracks()[0], contentAudioTrack]);
      window.meetingSession.audioVideo.enableSVCForContentShare(true);
      window.meetingSession.audioVideo.chooseVideoInputQuality(1, 1, 15, 20);
      window.meetingSession.audioVideo.setVideoMaxBandwidthKbps(20);
      window.meetingSession.audioVideo.setContentShareVideoCodecPreferences([
        window.ChimeSDK.VideoCodecCapability.vp9()
      ]);
      await window.meetingSession.audioVideo.startContentShare(contentStream);

      window.meetingSession.audioVideo.addObserver({
        audioVideoDidStop: (sessionStatus) => {
          window.restart();
        }
      });

        });
        await page.exposeFunction('restart', () => {
          onRestart();
        });
        meetingSession = page;

    res.json({ ok: true, message: 'Successfully joined meeting' })
  } catch (err) {
    console.error('Error joining chime meeting: ', err);
    res.status(500).json({ ok: false, error: 'Failed to join meeting: '+err.message });
  }
});

serverApp.post('/play-audio', async (req, res) => {
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


    window.ensureAudioGraph = function () {
      if (window.PlaybackElement) return;

      window.PlaybackElement = new Audio();
      window.PlaybackElement.loop = false;

      window.AudioSource = window.audioContext.createMediaStreamSource(window.musicElement);
      window.AudioGain = window.audioContext.createGain();
      window.AudioGain.gain.value = 1.0;

      window.AudioSource.connect(window.AudioGain);
      window.AudioGain.connect(window.audioDestination);
    };

    window.playMediaUrl = async function(url) {
      window.ensureAudioGraph();
      window.PlaybackElement.pause();
      window.PlaybackElement.currentTime = 0;
      window.PlaybackElement.src = url;
      await window.PlaybackElement.play();
    };

    window.stopMedia = function() {
      if (!window.PlaybackElement) return;
      window.PlaybackElement.pause();
      window.PlaybackElement.currentTime = 0;
    };

    await window.playMusicUrl(dataUrl)

  } catch (err) {
    console.error('Error playing audio: ', err);
    res.status(500).json({ ok: false, error: 'Failed to play audio: '+err.message });
  }
})

serverApp.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
