import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Eye, EyeClosed, LockKey } from "phosphor-react";
import { useState } from "react";
import reseticon from "@/assets/reseticon.png";

export default function SetNewPassword() {
  const [passwords, setPasswords] = useState({
    newPassword: "",
    confirmPassword: "",
  });
  const [showPassword, setShowPassword] = useState({
    new: false,
    confirm: false,
  });

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 h-screen overflow-hidden">
      {/* CSS to hide default browser password toggle icon */}
      <style>
        {`
          input[type="password"]::-ms-reveal,
          input[type="password"]::-ms-clear,
          input[type="password"]::-webkit-password-visibility-toggle {
            display: none;
          }
        `}
      </style>

      {/* Left Side - Form */}
      <div className="flex items-start justify-center md:ml-6 bg-white p-8 sm:py-34 h-full">
        <Card className="w-full max-w-md shadow-none border-0">
          <CardHeader>
            <CardTitle className="text-3xl font-bold text-orange-500">
              Set New Password
            </CardTitle>
            <p className="text-gray-500 text-sm">
              Please enter your new password and confirm it to update your
              account.
            </p>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-5">
              {/* New Password */}
              <div className="space-y-2.5">
                <Label htmlFor="newPassword">New Password *</Label>
                <div className="relative mt-2">
                  <LockKey
                    className="absolute left-2.5 top-2.5 h-5 w-5 text-gray-500"
                    weight="duotone"
                  />
                  <Input
                    id="newPassword"
                    type={showPassword.new ? "text" : "password"}
                    placeholder="***********"
                    value={passwords.newPassword}
                    onChange={(e) =>
                      setPasswords({ ...passwords, newPassword: e.target.value })
                    }
                    className="pl-10 pr-10 py-5 rounded-xl bg-[#F3F3F3] 
                      placeholder-shown:border-gray-300 
                      focus:border-orange-500 
                      not-placeholder-shown:border-orange-500 
                      focus:outline-none focus:ring-0 focus-visible:ring-0"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    aria-label={showPassword.new ? "Hide password" : "Show password"}
                    className="absolute right-2 top-1 h-8 px-2"
                    onClick={() =>
                      setShowPassword({ ...showPassword, new: !showPassword.new })
                    }
                  >
                    {showPassword.new ? (
                      <Eye size={22} weight="duotone" />
                    ) : (
                      <EyeClosed size={22} weight="duotone" />
                    )}
                  </Button>
                </div>
                <p className="text-sm font-medium text-gray-500">
                  Password must be{" "}
                  <span className="text-orange-500">6 characters long.</span>
                </p>
              </div>

              {/* Confirm Password */}
              <div className="space-y-2.5">
                <Label htmlFor="confirmPassword">Confirm Password *</Label>
                <div className="relative mt-2">
                  <LockKey
                    className="absolute left-2.5 top-2.5 h-5 w-5 text-gray-400"
                    weight="duotone"
                  />
                  <Input
                    id="confirmPassword"
                    type={showPassword.confirm ? "text" : "password"}
                    placeholder="***********"
                    value={passwords.confirmPassword}
                    onChange={(e) =>
                      setPasswords({
                        ...passwords,
                        confirmPassword: e.target.value,
                      })
                    }
                    className="pl-10 pr-10 py-5 rounded-xl bg-[#F3F3F3] 
                      placeholder-shown:border-gray-300 
                      focus:border-orange-500 
                      not-placeholder-shown:border-orange-500 
                      focus:outline-none focus:ring-0 focus-visible:ring-0"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    aria-label={
                      showPassword.confirm ? "Hide password" : "Show password"
                    }
                    className="absolute right-2 top-1 h-8 px-2"
                    onClick={() =>
                      setShowPassword({
                        ...showPassword,
                        confirm: !showPassword.confirm,
                      })
                    }
                  >
                    {showPassword.confirm ? (
                      <Eye size={20} weight="duotone" />
                    ) : (
                      <EyeClosed size={20} weight="duotone" />
                    )}
                  </Button>
                </div>
              </div>

              {/* Action Buttons */}
              <Button className="w-full bg-black text-white py-5 rounded-xl text-center">
                Update Password
              </Button>
              <Button
                variant="outline"
                className="w-full rounded-xl py-5 text-center"
              >
                Back to sign-in
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Right Side - Illustration */}
      <div className="hidden lg:flex mr-22 items-start justify-center p-0 pt-0 h-full relative">
        <div className="w-full h-screen flex items-end justify-end">
          <img
            src={reseticon}
            alt="Password reset illustration"
            className="w-auto max-h-[80%] object-contain absolute bottom-0 right-0"
          />
        </div>
      </div>
    </div>
  );
}
