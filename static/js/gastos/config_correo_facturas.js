document.addEventListener('DOMContentLoaded', () => {
  const emailInput = document.getElementById('id_email');
  const userInput = document.getElementById('id_username');
  const hostInput = document.getElementById('id_imap_host');

  if (!emailInput || !userInput || !hostInput) return;

  const hostByDomain = {
    'gmail.com': 'imap.gmail.com',
    'outlook.com': 'outlook.office365.com',
    'hotmail.com': 'outlook.office365.com',
    'live.com': 'outlook.office365.com',
    'yahoo.com': 'imap.mail.yahoo.com',
  };

  const suggestConfig = () => {
    const email = (emailInput.value || '').trim().toLowerCase();
    if (!email.includes('@')) return;

    const domain = email.split('@')[1];

    if (!userInput.value) {
      userInput.value = email;
    }

    if (!hostInput.value) {
      hostInput.value = hostByDomain[domain] || `imap.${domain}`;
    }
  };

  emailInput.addEventListener('blur', suggestConfig);
});
