// Real email validation — blocks disposable/fake domains
const REAL_EMAIL_REGEX = /^[a-zA-Z0-9._%+\-]+@(?!example\.com|test\.com|fake\.com|dummy\.com|mailnull\.com|trashmail\.com)[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$/;

export const validateEmail = (email) => {
  if (!email) return false;
  return REAL_EMAIL_REGEX.test(email);
};

export const validatePassword = (password) => {
  if (!password) return false;
  return password.length >= 8 && /[A-Za-z]/.test(password) && /[0-9]/.test(password);
};

export const passwordsMatch = (password, confirmPassword) => {
  return password === confirmPassword && confirmPassword.length > 0;
};

export const passwordStrength = (password) => {
  if (!password) return { score: -1, label: "" };
  let score = 0;
  if (password.length > 5) score += 1;
  if (password.length >= 8) score += 1;
  if (/[A-Z]/.test(password)) score += 1;
  if (/[0-9]/.test(password) && /[^A-Za-z0-9]/.test(password)) score += 1;

  // Max score 4, maps to index for strength-bars
  // 0/1: Weak (0), 2: Fair (1), 3: Good (2), 4: Strong (3)
  const scoreMap = [0, 0, 1, 2, 3];
  const finalScore = scoreMap[score];
  const labels = ["Weak", "Fair", "Good", "Strong"];

  return { score: finalScore, label: labels[finalScore] };
};
