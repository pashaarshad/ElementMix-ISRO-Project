
// Populate dropdowns with periodic elements
window.addEventListener('DOMContentLoaded', () => {
  if (typeof ELEMENTS !== 'undefined') {
    const el1 = document.getElementById('element1');
    const el2 = document.getElementById('element2');
    ELEMENTS.forEach(e => {
      const opt1 = document.createElement('option');
      opt1.value = e.symbol;
      opt1.textContent = `${e.name} (${e.symbol})`;
      el1.appendChild(opt1);
      const opt2 = document.createElement('option');
      opt2.value = e.symbol;
      opt2.textContent = `${e.name} (${e.symbol})`;
      el2.appendChild(opt2);
    });
  }
});

function cleanOutput(text) {
  // Remove stars, markdown, and limit to 5-10 lines
  let cleaned = text
    .replace(/\*\*([^*]+)\*\*/g, '$1') // remove bold markdown
    .replace(/\*/g, '') // remove single stars
    .replace(/[_`~]/g, '') // remove other markdown
    .replace(/#+/g, '') // remove heading markdown
    .replace(/\s{2,}/g, ' '); // collapse spaces
  let lines = cleaned.split(/\r?\n/).map(l => l.trim()).filter(Boolean);
  lines = lines.slice(0, 10); // max 10 lines
  return lines.join('\n');
}

async function getReaction() {
  let reactants = '';
  // Prefer R option if filled, else use dropdowns
  const rInput = document.getElementById('inputR').value.trim();
  if (rInput) {
    reactants = rInput;
  } else {
    const e1 = document.getElementById('element1').value;
    const e2 = document.getElementById('element2').value;
    if (e1 && e2) {
      reactants = `${e1}+${e2}`;
    }
  }
  if (!reactants) {
    document.getElementById('output').innerText = 'Please select or enter reactants.';
    return;
  }
  document.getElementById('output').innerText = 'Loading...';
  try {
    const res = await fetch('/get_reaction', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reactants })
    });
    const data = await res.json();
    if (data.error) {
      document.getElementById('output').innerText = data.error;
    } else {
      let result = '';
      if (data.source === 'local') {
        result = `ElementMix Result:\n${cleanOutput(data.equation)}\n${cleanOutput(data.explanation)}`;
      } else if (data.source === 'wolfram') {
        result = `ElementMix Result:\n${cleanOutput(data.equation)}`;
      } else if (data.source === 'ai') {
        result = `ElementMix Explanation:\n${cleanOutput(data.explanation)}`;
      }
      document.getElementById('output').innerText = result;
    }
  } catch (e) {
    document.getElementById('output').innerText = 'Error fetching reaction.';
  }
}

document.getElementById('reactBtn').onclick = getReaction;
