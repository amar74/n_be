import { z } from 'zod';
import { HTTPValidationError, ValidationError } from './generated/common';

export type HTTPValidationError = z.infer<typeof HTTPValidationError>
export type ValidationError = z.infer<typeof ValidationError>
