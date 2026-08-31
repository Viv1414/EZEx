// Lightweight client-side checks -- give instant feedback without a round
// trip to the backend. Not a substitute for server-side validation (the
// backend still enforces its own rules on every request regardless).

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function isValidEmail(email: string): boolean {
  return EMAIL_PATTERN.test(email);
}

export const MIN_PASSWORD_LENGTH = 8;
export const MAX_PASSWORD_LENGTH = 30;

export function isValidPasswordLength(password: string): boolean {
  return password.length >= MIN_PASSWORD_LENGTH && password.length <= MAX_PASSWORD_LENGTH;
}

export const MIN_PROGRAM_NAME_LENGTH = 4;
export const MAX_PROGRAM_NAME_LENGTH = 25;

export function isValidProgramName(name: string): boolean {
  return name.length >= MIN_PROGRAM_NAME_LENGTH && name.length <= MAX_PROGRAM_NAME_LENGTH;
}
