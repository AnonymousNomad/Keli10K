(function() {
  'use strict';

  function generate(taskName) {
    const userName = 'Developer';
    const date = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });

    const canvas = document.createElement('canvas');
    canvas.width = 800;
    canvas.height = 600;
    const ctx = canvas.getContext('2d');

    // Background - deep glacial
    ctx.fillStyle = '#0a1628';
    ctx.fillRect(0, 0, 800, 600);

    // Border - aurora glow
    ctx.strokeStyle = '#00e5ff';
    ctx.lineWidth = 2;
    ctx.strokeRect(20, 20, 760, 560);

    // Inner border
    ctx.strokeStyle = '#1a4b5c';
    ctx.lineWidth = 1;
    ctx.strokeRect(30, 30, 740, 540);

    // Title
    ctx.fillStyle = '#00e5ff';
    ctx.font = 'bold 36px "Georgia", serif';
    ctx.textAlign = 'center';
    ctx.fillText('KELI CERTIFIED DEVELOPER', 400, 120);

    // Line
    ctx.strokeStyle = '#00e5ff';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(200, 145);
    ctx.lineTo(600, 145);
    ctx.stroke();

    // Subtitle
    ctx.fillStyle = '#c0d6e4';
    ctx.font = '18px "Georgia", serif';
    ctx.fillText('This certifies that', 400, 190);

    // User name
    ctx.fillStyle = '#00ffc8';
    ctx.font = 'bold 28px "Georgia", serif';
    ctx.fillText(userName, 400, 235);

    // Completed task
    ctx.fillStyle = '#c0d6e4';
    ctx.font = '16px "Georgia", serif';
    ctx.fillText('has successfully completed', 400, 275);

    ctx.fillStyle = '#b967ff';
    ctx.font = 'bold 22px "Georgia", serif';
    ctx.fillText(taskName, 400, 315);

    // Date
    ctx.fillStyle = '#4a6b7c';
    ctx.font = '14px "Georgia", serif';
    ctx.fillText('on this day ' + date, 400, 365);

    // Fish logo (Keli fish)
    ctx.save();
    ctx.translate(400, 440);
    ctx.fillStyle = '#00e5ff';
    ctx.beginPath();
    ctx.moveTo(0, -20);
    ctx.lineTo(15, 0);
    ctx.lineTo(0, 20);
    ctx.lineTo(-5, 10);
    ctx.lineTo(-20, 0);
    ctx.lineTo(-5, -10);
    ctx.closePath();
    ctx.fill();
    ctx.fillStyle = '#00ffc8';
    ctx.beginPath();
    ctx.arc(3, -2, 4, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    // Signature line
    ctx.strokeStyle = '#1a4b5c';
    ctx.beginPath();
    ctx.moveTo(280, 500);
    ctx.lineTo(520, 500);
    ctx.stroke();
    ctx.fillStyle = '#4a6b7c';
    ctx.font = '12px "Georgia", serif';
    ctx.fillText('Keli AI - Swarm Neural Computer Architecture', 400, 520);

    // Border decorations - aurora lines
    for (let i = 0; i < 20; i++) {
      const x = 40 + i * 38;
      ctx.fillStyle = `rgba(0, 229, 255, ${0.05 + Math.random() * 0.1})`;
      ctx.fillRect(x, 35, 2, 8);
      ctx.fillRect(x, 557, 2, 8);
    }

    // Convert to data URL and download
    const dataUrl = canvas.toDataURL('image/png');

    // Save to IndexedDB
    saveToDB({
      id: Date.now(),
      task: taskName,
      user: userName,
      date: date,
      dataUrl: dataUrl,
    });

    // Trigger download
    const link = document.createElement('a');
    link.download = `keli-certificate-${taskName.replace(/\s+/g, '-').toLowerCase()}.png`;
    link.href = dataUrl;
    link.click();

    // Show in chat
    if (window.KeliChat) {
      window.KeliChat.addMessage('keli', `Certificate generated! Check your downloads.`, { type: 'success' });
    }
  }

  function saveToDB(cert) {
    try {
      const request = indexedDB.open('KeliCertificates', 1);
      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        if (!db.objectStoreNames.contains('certs')) {
          db.createObjectStore('certs', { keyPath: 'id' });
        }
      };
      request.onsuccess = (event) => {
        const db = event.target.result;
        const tx = db.transaction('certs', 'readwrite');
        tx.objectStore('certs').put(cert);
      };
    } catch (e) {
      console.log('Certificate storage failed:', e.message);
    }
  }

  function listCerts(callback) {
    try {
      const request = indexedDB.open('KeliCertificates', 1);
      request.onsuccess = (event) => {
        const db = event.target.result;
        const tx = db.transaction('certs', 'readonly');
        const all = tx.objectStore('certs').getAll();
        all.onsuccess = () => callback(all.result || []);
      };
    } catch (e) {
      callback([]);
    }
  }

  window.KeliCertificate = { generate, listCerts };
})();
