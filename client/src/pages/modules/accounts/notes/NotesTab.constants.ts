export const DEFAULT_FORM_VALUES = {
  title: '',
  content: '',
  date: new Date().toISOString(), // Today's date in YYYY-MM-DD format
} as const;
