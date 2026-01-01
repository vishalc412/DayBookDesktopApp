/**
 * Format API error response for display
 * Handles both simple string errors and Pydantic validation error arrays
 */
export const formatErrorMessage = (error) => {
  // If it's a simple string, return it
  if (typeof error === 'string') {
    return error;
  }

  // If it's an axios error response
  if (error.response?.data) {
    const { detail } = error.response.data;

    // If detail is a string, return it
    if (typeof detail === 'string') {
      return detail;
    }

    // If detail is an array of validation errors (Pydantic format)
    if (Array.isArray(detail)) {
      return detail.map(err => {
        const field = err.loc ? err.loc.join('.') : 'unknown';
        return `${field}: ${err.msg}`;
      }).join('; ');
    }

    // If detail is an object with validation errors
    if (typeof detail === 'object') {
      return JSON.stringify(detail);
    }
  }

  // Fallback to error message
  return error.message || 'An unexpected error occurred';
};
