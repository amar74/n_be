import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Envelope, Lock, Eye, EyeClosed, House, CaretRight } from "phosphor-react";
import { useState } from "react";
import { ResetPasswordDialog } from "./ResetPasswordDialog";
import Frame from "@/assets/Frame.png";

export default function SignInPage() {
  const [showPassword, setShowPassword] = useState(true);

  const handleSubmit = (e: { preventDefault: () => void }) => {
    e.preventDefault();
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 h-screen overflow-x-hidden">
      {/* Hide default browser password toggle icon */}
      <style>
        {`
          input[type="password"]::-ms-reveal,
          input[type="password"]::-ms-clear,
          input[type="password"]::-webkit-password-visibility-toggle {
            display: none;
          }
        `}
      </style>

      {/* Left: Sign In Form */}
      <div className="flex sm:ml-10 sm:mb-5 items-center justify-center bg-white">
        <Card className="w-full max-w-md shadow-none border-0">
          <CardHeader className="space-y-2">
            <div className="flex flex-row items-center gap-1">
              <House size={20} className="text-gray-700" />
              <CaretRight size={16} className="text-gray-700" />
              <p className="text-md font-medium text-gray-900">Sign-in</p>
            </div>
            <CardTitle className="text-3xl font-bold text-[#ED8A09]">
              Sign In
            </CardTitle>
            <p className="text-gray-400 text-sm font-sans">
              Enter your email and password to sign in
            </p>
          </CardHeader>

          <CardContent className="space-y-6">
            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Email */}
              <div className="space-y-2.5">
                <Label htmlFor="email">Email *</Label>
                <div className="relative mt-2">
                  <Envelope
                    className="absolute left-2 top-2 h-5 w-5 text-gray-400"
                    weight="duotone"
                  />
                  <Input
                    id="email"
                    type="email"
                    placeholder="johndoe46@gmail.com"
                    className="pl-10 pr-3 py-2 rounded-xl
                      placeholder-shown:border-gray-300
                      focus:border-[#ED8A09]
                      not-placeholder-shown:border-[#ED8A09]
                      focus:outline-none focus:ring-0 focus-visible:ring-0"
                    required
                  />
                </div>
              </div>

              {/* Password */}
              <div className="space-y-2.5">
                <Label htmlFor="password" className="text-sm">
                  Password *
                </Label>
                <div className="relative mt-2">
                  <Lock
                    className="absolute left-2 top-2 h-5 w-5 text-gray-400"
                    weight="duotone"
                  />
                  <Input
                    id="password"
                    type={showPassword ? "password" : "text"}
                    placeholder="********"
                    className="pl-10 pr-10 py-2 rounded-xl
                      placeholder-shown:border-gray-300
                      focus:border-[#ED8A09]
                      not-placeholder-shown:border-[#ED8A09]
                      focus:outline-none focus:ring-0 focus-visible:ring-0"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-2.5 text-gray-500"
                    aria-label={showPassword ? "Show password" : "Hide password"}
                  >
                    {showPassword ? (
                      <EyeClosed size={20} weight="duotone" />
                    ) : (
                      <Eye size={20} weight="duotone" />
                    )}
                  </button>
                </div>
              </div>

              {/* Options */}
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center space-x-2">
                  <Checkbox id="keep-logged" className="border-[#ED8A09]" />
                  <Label htmlFor="keep-logged" className="text-[#ED8A09]">
                    Keep me logged in
                  </Label>
                </div>
                <ResetPasswordDialog />
              </div>

              {/* Submit */}
              <Button
                type="submit"
                className="w-full bg-black text-white py-2 rounded-xl"
              >
                Sign-in
              </Button>
            </form>

            {/* Footer */}
            <p className="text-sm text-gray-500">
              Don’t have an account?{" "}
              <a
                href="/contact"
                className="text-[#ED8A09] font-medium hover:underline"
              >
                Contact Sales
              </a>
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Right: Brand Info */}
      <div className="hidden md:flex flex-row justify-end items-center relative overflow-hidden">
        <img
          src={Frame}
          alt="Megapolis Advisory logo"
          className="max-h-screen object-cover"
        />
      </div>
    </div>
  );
}
