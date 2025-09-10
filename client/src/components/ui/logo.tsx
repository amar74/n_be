import React from "react";

interface LogoProps {
  className?: string;
}

export function Logo({ className = "h-6 w-6" }: LogoProps) {
  return (
    <img
      src="https://cdn.builder.io/api/v1/image/assets%2Fb387cb49d72f4e48991d040ce39c93a2%2F17d2ca3c6b8e498cb782f33762da3c06?format=webp&width=800"
      alt="Megapolis Technologies Logo"
      className={`${className} object-contain`}
    />
  );
}

// Alternative simplified version
export function LogoSimple({ className = "h-6 w-6" }: LogoProps) {
  return (
    <svg
      viewBox="0 0 32 32"
      fill="currentColor"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Simplified M-shaped Mobius */}
      <path
        d="M4,28 L4,8 Q4,4 8,4 Q12,4 12,8 L12,16 Q14,12 16,16 Q18,12 20,16 L20,8 Q20,4 24,4 Q28,4 28,8 L28,28"
        stroke="currentColor"
        strokeWidth="2.5"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
      />

      {/* Mobius twist */}
      <path
        d="M12,16 Q14,8 16,12 Q18,16 20,8"
        stroke="currentColor"
        strokeWidth="2.5"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
