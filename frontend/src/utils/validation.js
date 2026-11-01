/**
 * @fileoverview validation.js - Reusable Form Field Validation Utilities
 * @module utils/validation
 * @version 1.0.0
 * @author Antigravity Pair Programmer
 * 
 * Responsibilities:
 * - Provide pure utility functions for validating field inputs (email, password, name, required).
 * - Compute password strength scores and user-facing complexity feedback.
 * - Enforce clean, predictable output shapes for all validators.
 * - Prevent throw exceptions on invalid input types.
 * 
 * Exported APIs:
 * - validateRequired(value, fieldName)
 * - validateEmail(email)
 * - validatePassword(password)
 * - getPasswordStrength(password)
 * - validateConfirmPassword(password, confirmPassword)
 * - validateFullName(name)
 * 
 * Constants:
 * - EMAIL_REGEX
 * - PASSWORD_REGEX
 * - NAME_REGEX
 * - PASSWORD_STRENGTH_LEVELS
 * 
 * Dependencies:
 * - None (Native Standard Web APIs only)
 */

/**
 * Regular expression to match standard email patterns.
 * @type {RegExp}
 */
export const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/**
 * Regular expression for complex password validation:
 * Minimum 8 characters, at least one uppercase letter, one lowercase letter,
 * one numeric digit, and one special character from the set [@$!%*?&].
 * @type {RegExp}
 */
export const PASSWORD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;

/**
 * Regular expression for validating names:
 * Consists of alphabetic characters and can include spaces, hyphens, and apostrophes.
 * Starts and ends with a letter.
 * @type {RegExp}
 */
export const NAME_REGEX = /^[A-Za-z]+(?:[ '-][A-Za-z]+)*$/;

/**
 * Centralized password strength level strings.
 * @type {object}
 */
export const PASSWORD_STRENGTH_LEVELS = {
  WEAK: 'weak',
  MEDIUM: 'medium',
  STRONG: 'strong'
};

/**
 * Validates that a value is provided and is not empty, null, undefined, or whitespace-only.
 * 
 * @param {*} value - The input value to check.
 * @param {string} fieldName - The human-readable name of the field.
 * @returns {object} Standardized validation result { isValid, error }.
 * @example
 * const res = validateRequired("", "Email"); // { isValid: false, error: "Email is required." }
 */
export const validateRequired = (value, fieldName) => {
  const normalizedFieldName = fieldName || 'Field';
  
  if (value === null || value === undefined) {
    return {
      isValid: false,
      error: `${normalizedFieldName} is required.`
    };
  }

  const stringValue = String(value).trim();
  if (stringValue === '') {
    return {
      isValid: false,
      error: `${normalizedFieldName} is required.`
    };
  }

  return {
    isValid: true,
    error: null
  };
};

/**
 * Validates that an email matches the standard pattern.
 * 
 * @param {string} email - The email address to validate.
 * @returns {object} Standardized validation result { isValid, error }.
 * @example
 * const res = validateEmail("user@domain.com"); // { isValid: true, error: null }
 */
export const validateEmail = (email) => {
  const requiredCheck = validateRequired(email, 'Email');
  if (!requiredCheck.isValid) {
    return requiredCheck;
  }

  const emailStr = String(email);
  if (!EMAIL_REGEX.test(emailStr)) {
    return {
      isValid: false,
      error: 'Please enter a valid email address.'
    };
  }

  return {
    isValid: true,
    error: null
  };
};

/**
 * Validates that a password satisfies the base strength rules:
 * Minimum 8 characters, at least one uppercase letter, one lowercase letter,
 * one number, and one special character.
 * 
 * @param {string} password - The password string to validate.
 * @returns {object} Standardized validation result { isValid, error }.
 * @example
 * const res = validatePassword("Pass123!"); // { isValid: true, error: null }
 */
export const validatePassword = (password) => {
  const requiredCheck = validateRequired(password, 'Password');
  if (!requiredCheck.isValid) {
    return requiredCheck;
  }

  const passwordStr = String(password);
  if (!PASSWORD_REGEX.test(passwordStr)) {
    return {
      isValid: false,
      error: 'Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one number, and one special character.'
    };
  }

  return {
    isValid: true,
    error: null
  };
};

/**
 * Evaluates the structural complexity of a password and returns a score and descriptive level.
 * Never throws exceptions.
 * 
 * @param {string} password - The password string to analyze.
 * @returns {object} Evaluation results containing { isValid, score, level, feedback }.
 * @example
 * const res = getPasswordStrength("weak"); // { isValid: false, score: 1, level: "weak", feedback: "..." }
 */
export const getPasswordStrength = (password) => {
  if (password === null || password === undefined || String(password).trim() === '') {
    return {
      isValid: false,
      score: 0,
      level: PASSWORD_STRENGTH_LEVELS.WEAK,
      feedback: 'Password is required.'
    };
  }

  const passwordStr = String(password);
  let score = 0;
  const feedbackList = [];

  // Criterion 1: Length
  if (passwordStr.length >= 8) {
    score += 1;
  } else {
    feedbackList.push('Add more characters (min 8).');
  }

  if (passwordStr.length >= 12) {
    score += 1;
  }

  // Criterion 2: Lowercase character
  if (/[a-z]/.test(passwordStr)) {
    score += 1;
  } else {
    feedbackList.push('Add a lowercase letter.');
  }

  // Criterion 3: Uppercase character
  if (/[A-Z]/.test(passwordStr)) {
    score += 1;
  } else {
    feedbackList.push('Add an uppercase letter.');
  }

  // Criterion 4: Number
  if (/\d/.test(passwordStr)) {
    score += 1;
  } else {
    feedbackList.push('Add a number.');
  }

  // Criterion 5: Special character
  if (/[@$!%*?&]/.test(passwordStr)) {
    score += 1;
  } else {
    feedbackList.push('Add a special character (e.g., @, $, !, %, *, ?, &).');
  }

  // Map score to levels
  let level = PASSWORD_STRENGTH_LEVELS.WEAK;
  if (score >= 5) {
    level = PASSWORD_STRENGTH_LEVELS.STRONG;
  } else if (score >= 3) {
    level = PASSWORD_STRENGTH_LEVELS.MEDIUM;
  }

  const isValid = score >= 5 && passwordStr.length >= 8;
  const feedback = feedbackList.length > 0 ? feedbackList.join(' ') : null;

  return {
    isValid,
    score,
    level,
    feedback
  };
};

/**
 * Validates that the confirmation password is identical to the primary password.
 * 
 * @param {string} password - The primary password.
 * @param {string} confirmPassword - The password confirmation string.
 * @returns {object} Standardized validation result { isValid, error }.
 * @example
 * const res = validateConfirmPassword("Pass123!", "Pass123!"); // { isValid: true, error: null }
 */
export const validateConfirmPassword = (password, confirmPassword) => {
  const passwordCheck = validateRequired(password, 'Password');
  if (!passwordCheck.isValid) {
    return {
      isValid: false,
      error: 'Password is required to confirm.'
    };
  }

  if (confirmPassword === null || confirmPassword === undefined || String(confirmPassword) === '') {
    return {
      isValid: false,
      error: 'Please confirm your password.'
    };
  }

  if (String(password) !== String(confirmPassword)) {
    return {
      isValid: false,
      error: 'Passwords do not match.'
    };
  }

  return {
    isValid: true,
    error: null
  };
};

/**
 * Validates a full name input for valid characters and length constraints.
 * 
 * @param {string} name - The name string to check.
 * @returns {object} Standardized validation result { isValid, error }.
 * @example
 * const res = validateFullName("Jane Doe"); // { isValid: true, error: null }
 */
export const validateFullName = (name) => {
  const requiredCheck = validateRequired(name, 'Full name');
  if (!requiredCheck.isValid) {
    return requiredCheck;
  }

  const nameStr = String(name).trim();

  if (nameStr.length < 2) {
    return {
      isValid: false,
      error: 'Full name must be at least 2 characters long.'
    };
  }

  if (nameStr.length > 100) {
    return {
      isValid: false,
      error: 'Full name cannot exceed 100 characters.'
    };
  }

  if (!NAME_REGEX.test(nameStr)) {
    return {
      isValid: false,
      error: 'Full name can only contain letters, spaces, hyphens, and apostrophes, and cannot start or end with spaces/punctuation.'
    };
  }

  return {
    isValid: true,
    error: null
  };
};