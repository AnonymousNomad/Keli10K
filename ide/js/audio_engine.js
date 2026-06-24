(function() {
  'use strict';

  let ctx = null;
  let masterGain = null;
  let analyser = null;
  let currentState = 'idle';
  let volume = 0.5;
  let isMuted = false;
  let bpm = 80;
  let beatInterval = null;
  let initialized = false;

  // Classical layer
  let arpOsc = null;
  let arpGain = null;
  let arpInterval = null;
  let arpNotes = [220, 261, 329, 392, 440, 523, 659, 784];

  // Hip-hop layer
  let beatCount = 0;
  let kickGain = null;
  let snareGain = null;
  let hihatGain = null;

  // Ambient layer
  let padOsc1 = null;
  let padOsc2 = null;
  let padGain = null;
  let padFilter = null;
  let lfoGain = null;

  function isAudioSupported() {
    return typeof AudioContext !== 'undefined' || typeof webkitAudioContext !== 'undefined';
  }

  function init() {
    if (initialized) return;
    if (!isAudioSupported()) {
      console.log('Audio engine: Web Audio API not supported');
      return;
    }

    try {
      const AC = window.AudioContext || window.webkitAudioContext;
      ctx = new AC();

      masterGain = ctx.createGain();
      masterGain.gain.value = volume;
      masterGain.connect(ctx.destination);

      analyser = ctx.createAnalyser();
      analyser.fftSize = 256;
      masterGain.connect(analyser);

      initialized = true;
      console.log('Audio engine initialized');
    } catch (e) {
      console.log('Audio engine init failed:', e.message);
    }
  }

  function startClassical() {
    if (!ctx || arpInterval) return;

    arpGain = ctx.createGain();
    arpGain.gain.value = 0.08;
    arpGain.connect(masterGain);

    arpOsc = ctx.createOscillator();
    arpOsc.type = 'sine';
    arpOsc.frequency.value = 440;
    arpOsc.connect(arpGain);
    arpOsc.start();

    let noteIndex = 0;
    arpInterval = setInterval(() => {
      if (currentState === 'idle' || currentState === 'tutor') {
        bpm = Math.max(80, bpm - 0.5);
      } else if (currentState === 'typing' || currentState === 'building') {
        bpm = Math.min(120, bpm + 0.5);
      }

      const baseNote = arpNotes[Math.floor(Math.random() * arpNotes.length)];
      const pentatonic = [0, 2, 4, 7, 9];
      const offset = pentatonic[Math.floor(Math.random() * pentatonic.length)];
      const freq = baseNote * Math.pow(2, offset / 12);
      arpOsc.frequency.setTargetAtTime(freq, ctx.currentTime, 0.05);

      const intervalMs = 60000 / bpm;
      clearInterval(arpInterval);
      arpInterval = setInterval(() => {
        const nextFreq = baseNote * Math.pow(2, pentatonic[Math.floor(Math.random() * pentatonic.length)] / 12);
        arpOsc.frequency.setTargetAtTime(nextFreq, ctx.currentTime, 0.05);
      }, intervalMs);

    }, 60000 / bpm);
  }

  function stopClassical() {
    if (arpInterval) {
      clearInterval(arpInterval);
      arpInterval = null;
    }
    if (arpOsc) {
      try { arpOsc.stop(); } catch(e) {}
      arpOsc = null;
    }
    if (arpGain) {
      arpGain.disconnect();
      arpGain = null;
    }
  }

  function playKick(time) {
    if (!ctx) return;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(150, time);
    osc.frequency.exponentialRampToValueAtTime(30, time + 0.08);
    gain.gain.setValueAtTime(0.3, time);
    gain.gain.exponentialRampToValueAtTime(0.001, time + 0.1);
    osc.connect(gain);
    gain.connect(masterGain);
    osc.start(time);
    osc.stop(time + 0.1);
  }

  function playSnare(time) {
    if (!ctx) return;
    const bufferSize = ctx.sampleRate * 0.05;
    const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
      data[i] = (Math.random() * 2 - 1) * Math.exp(-i / (bufferSize * 0.15));
    }
    const source = ctx.createBufferSource();
    source.buffer = buffer;
    const gain = ctx.createGain();
    gain.gain.setValueAtTime(0.2, time);
    gain.gain.exponentialRampToValueAtTime(0.001, time + 0.1);
    const filter = ctx.createBiquadFilter();
    filter.type = 'highpass';
    filter.frequency.value = 2000;
    source.connect(filter);
    filter.connect(gain);
    gain.connect(masterGain);
    source.start(time);
    source.stop(time + 0.1);
  }

  function playHihat(time) {
    if (!ctx) return;
    const bufferSize = ctx.sampleRate * 0.02;
    const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
      data[i] = (Math.random() * 2 - 1) * Math.exp(-i / (bufferSize * 0.2));
    }
    const source = ctx.createBufferSource();
    source.buffer = buffer;
    const gain = ctx.createGain();
    gain.gain.setValueAtTime(0.1, time);
    gain.gain.exponentialRampToValueAtTime(0.001, time + 0.05);
    const filter = ctx.createBiquadFilter();
    filter.type = 'highpass';
    filter.frequency.value = 8000;
    source.connect(filter);
    filter.connect(gain);
    gain.connect(masterGain);
    source.start(time);
    source.stop(time + 0.05);
  }

  function startDrums() {
    if (beatInterval || !ctx) return;

    beatInterval = setInterval(() => {
      const now = ctx.currentTime;
      const swing = Math.random() * 0.01;

      if (beatCount % 4 === 0) {
        playKick(now + swing);
      }
      if (beatCount % 4 === 2) {
        playKick(now + swing);
      }
      if (beatCount % 2 === 1) {
        playSnare(now + swing);
      }
      if (beatCount % 2 === 0) {
        playHihat(now);
      }

      beatCount = (beatCount + 1) % 8;
    }, 60000 / bpm / 2);
  }

  function stopDrums() {
    if (beatInterval) {
      clearInterval(beatInterval);
      beatInterval = null;
    }
    beatCount = 0;
  }

  function startAmbient() {
    if (!ctx || padOsc1) return;

    padGain = ctx.createGain();
    padGain.gain.value = 0.04;
    padGain.connect(masterGain);

    padFilter = ctx.createBiquadFilter();
    padFilter.type = 'lowpass';
    padFilter.frequency.value = 800;
    padFilter.Q.value = 1;
    padGain.connect(padFilter);
    padFilter.connect(masterGain);

    padOsc1 = ctx.createOscillator();
    padOsc1.type = 'sawtooth';
    padOsc1.frequency.value = 220;
    padOsc1.connect(padGain);
    padOsc1.start();

    padOsc2 = ctx.createOscillator();
    padOsc2.type = 'sine';
    padOsc2.frequency.value = 442;
    padOsc2.connect(padGain);
    padOsc2.start();

    lfoGain = ctx.createGain();
    lfoGain.gain.value = 200;
    const lfo = ctx.createOscillator();
    lfo.type = 'sine';
    lfo.frequency.value = 0.1;
    lfo.connect(lfoGain);
    lfoGain.connect(padFilter.frequency);
    lfo.start();
  }

  function stopAmbient() {
    if (padOsc1) { try { padOsc1.stop(); } catch(e) {} padOsc1 = null; }
    if (padOsc2) { try { padOsc2.stop(); } catch(e) {} padOsc2 = null; }
    if (padGain) { padGain.disconnect(); padGain = null; }
    if (padFilter) { padFilter.disconnect(); padFilter = null; }
    if (lfoGain) { lfoGain.disconnect(); lfoGain = null; }
  }

  function setState(newState) {
    if (!initialized || !ctx) return;
    if (newState === currentState) return;

    currentState = newState;

    switch (newState) {
      case 'idle':
        bpm = 80;
        stopDrums();
        stopClassical();
        startAmbient();
        break;

      case 'typing':
        bpm = 100;
        startClassical();
        startDrums();
        startAmbient();
        break;

      case 'building':
        bpm = 120;
        startClassical();
        startDrums();
        startAmbient();
        // Ensure resume context
        if (ctx.state === 'suspended') ctx.resume();
        break;

      case 'success':
        // Play a satisfying chord
        if (ctx) {
          [261, 329, 392].forEach((freq, i) => {
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = 'sine';
            osc.frequency.value = freq;
            gain.gain.setValueAtTime(0.2, ctx.currentTime + i * 0.05);
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 1.5);
            osc.connect(gain);
            gain.connect(masterGain);
            osc.start(ctx.currentTime + i * 0.05);
            osc.stop(ctx.currentTime + 2);
          });
        }
        break;

      case 'error':
        // Dissonant tone + stutter
        if (ctx) {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'square';
          osc.frequency.value = 200;
          gain.gain.setValueAtTime(0.1, ctx.currentTime);
          gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.3);
          osc.connect(gain);
          gain.connect(masterGain);
          osc.start(ctx.currentTime);
          osc.stop(ctx.currentTime + 0.5);
        }
        break;

      case 'tutor':
        bpm = 85;
        startClassical();
        startAmbient();
        stopDrums();
        break;
    }
  }

  function setVolume(val) {
    volume = Math.max(0, Math.min(1, val));
    if (masterGain) {
      masterGain.gain.value = isMuted ? 0 : volume;
    }
  }

  function mute() {
    isMuted = true;
    if (masterGain) masterGain.gain.value = 0;
  }

  function unmute() {
    isMuted = false;
    if (masterGain) masterGain.gain.value = volume;
  }

  function destroy() {
    stopClassical();
    stopDrums();
    stopAmbient();
    if (beatInterval) { clearInterval(beatInterval); beatInterval = null; }
    if (ctx) {
      ctx.close().catch(() => {});
      ctx = null;
    }
    initialized = false;
  }

  function getAnalyser() { return analyser; }
  function getState() { return currentState; }
  function isInitialized() { return initialized; }

  window.KeliAudio = {
    init, setState, setVolume, mute, unmute, destroy,
    getAnalyser, getState, isInitialized,
  };
})();
