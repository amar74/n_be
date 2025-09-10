import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Mail } from 'lucide-react';

interface SuccessMessageProps {
  email: string;
  onGoToLogin: () => void;
}

export function SuccessMessage({ email, onGoToLogin }: SuccessMessageProps) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 p-3 bg-green-100 rounded-full w-fit">
            <Mail className="h-6 w-6 text-green-600" />
          </div>
          <CardTitle className="text-2xl font-bold text-[#1D1D1F]">
            Check Your Email
          </CardTitle>
          <CardDescription>
            We've sent you a confirmation email at <strong>{email}</strong>. 
            Please click the link in the email to activate your account.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button
            onClick={onGoToLogin}
            className="w-full bg-[#0D9488] hover:bg-[#0D9488]/90"
          >
            Go to Login
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
