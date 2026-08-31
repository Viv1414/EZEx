// Lightweight client-side checks -- give instant feedback without a round
// trip to the backend. Not a substitute for server-side validation (the
// backend still enforces its own rules on every request regardless).

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function isValidEmail(email: string): boolean {
  return EMAIL_PATTERN.test(email);
}

export const MIN_PASSWORD_LENGTH = 8;
// Kept in sync with backend/app/schemas/user.py's MAX_PASSWORD_LENGTH --
// 72 matches bcrypt's own byte limit exactly. That only works as a
// character count because passwords are restricted to printable ASCII
// (see isValidPasswordCharset), where every character is exactly 1 byte.
export const MAX_PASSWORD_LENGTH = 72;

export function isValidPasswordLength(password: string): boolean {
  return password.length >= MIN_PASSWORD_LENGTH && password.length <= MAX_PASSWORD_LENGTH;
}

// Printable ASCII only (space through ~) -- standard keyboard characters,
// no emoji/accented letters. Mirrors backend/app/schemas/user.py's
// _validate_password_charset; matches its ord() range exactly.
const PASSWORD_CHARSET_PATTERN = /^[\x20-\x7E]*$/;

export function isValidPasswordCharset(password: string): boolean {
  return PASSWORD_CHARSET_PATTERN.test(password);
}

export const MIN_PROGRAM_NAME_LENGTH = 4;
export const MAX_PROGRAM_NAME_LENGTH = 25;

export function isValidProgramName(name: string): boolean {
  return name.length >= MIN_PROGRAM_NAME_LENGTH && name.length <= MAX_PROGRAM_NAME_LENGTH;
}

const PROGRAM_CHARSET_PATTERN = /^[\x20-\x7E]*$/;

export function isValidProgramCharset(name: string): boolean {
  return PROGRAM_CHARSET_PATTERN.test(name);
}