// Mirrors backend/app/schemas/user.py:UserRead
export interface User {
  id: number;
  email: string;
  is_verified: boolean;
  created_at: string;
}
