import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface ErrorCardProps {
  error?: string | null;
  onGoToLogin: () => void;
}

export function ErrorCard({ error, onGoToLogin }: ErrorCardProps) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-center text-red-600">Invitation Error</CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          <div className="text-center py-4 space-y-4">
            <p className="text-red-600">
              {error || "Something went wrong with your invitation."}
            </p>
            {error && (
              <details className="text-left">
                <summary className="text-sm text-gray-600 cursor-pointer">Show Details</summary>
                <pre className="text-xs text-gray-500 mt-2 bg-gray-100 p-2 rounded overflow-auto">
                  {error}
                </pre>
              </details>
            )}
            <Button
              onClick={onGoToLogin}
              variant="outline"
            >
              Go to Login
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
