import { Card, CardContent } from '@/components/ui/card';
import { Loader2 } from 'lucide-react';

interface LoadingCardProps {
  message: string;
}

export function LoadingCard({ message }: LoadingCardProps) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <Card className="w-full max-w-md">
        <CardContent className="p-6">
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-8 w-8 animate-spin text-[#0D9488]" />
            <span className="ml-2 text-[#1D1D1F]/70">{message}</span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
