"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  sendVerificationCode,
  resendVerificationCode,
  verifyEmail,
  registerUser,
} from "@/lib/auth/auth";

export default function RegisterPage() {
  const router = useRouter();

  const [step, setStep] = useState(1);

  const [email, setEmail] = useState("");
  const [verificationToken, setVerificationToken] = useState("");

  const [code, setCode] = useState("");

  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [password2, setPassword2] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const handleSendCode = async (e: React.FormEvent) => {
    e.preventDefault();

    setLoading(true);
    setError("");
    setSuccessMessage("");

    try {
      const data = await sendVerificationCode(email);

      setVerificationToken(data.user_verify_token);
      setEmail(data.user_verify_email);

      setSuccessMessage(data.message);
      setStep(2);
    } catch (err: any) {
      setError(
        err?.response?.data?.error ||
          "Failed to send verification code."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyCode = async (e: React.FormEvent) => {
    e.preventDefault();

    setLoading(true);
    setError("");
    setSuccessMessage("");

    try {
      const data = await verifyEmail(
        code,
        verificationToken
      );

      setSuccessMessage(data.message);
      setStep(3);
    } catch (err: any) {
      setError(
        err?.response?.data?.error ||
          "Verification failed."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleResendCode = async () => {
    setLoading(true);
    setError("");
    setSuccessMessage("");

    try {
      const data = await resendVerificationCode(email);

      setSuccessMessage(
        data.message || "Verification code resent."
      );
    } catch (err: any) {
      setError(
        err?.response?.data?.error ||
          "Failed to resend code."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (
    e: React.FormEvent
  ) => {
    e.preventDefault();

    setLoading(true);
    setError("");
    setSuccessMessage("");

    try {
      const data = await registerUser({
        email,
        full_name: fullName,
        password,
        password2,
      });

      setSuccessMessage(data.message);

      setTimeout(() => {
        router.push("/login");
      }, 1000);
    } catch (err: any) {
      const responseData = err?.response?.data;

      if (typeof responseData === "object") {
        const firstError = Object.values(
          responseData
        )[0];

        if (Array.isArray(firstError)) {
          setError(firstError[0]);
        } else {
          setError(String(firstError));
        }
      } else {
        setError("Registration failed.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
      <div className="w-full max-w-md bg-white border rounded-2xl shadow-sm p-8">
        <div className="mb-8">
          <h1 className="text-2xl font-semibold text-gray-900">
            Create Account
          </h1>

          <p className="text-sm text-gray-500 mt-1">
            Build powerful workflow automations.
          </p>
        </div>

        {/* Progress */}
        <div className="flex items-center gap-2 mb-8">
          <Step active={step >= 1}>Email</Step>
          <Step active={step >= 2}>Verify</Step>
          <Step active={step >= 3}>Account</Step>
        </div>

        {error && (
          <div className="mb-4 text-sm text-red-500">
            {error}
          </div>
        )}

        {successMessage && (
          <div className="mb-4 text-sm text-green-600">
            {successMessage}
          </div>
        )}

        {/* STEP 1 */}
        {step === 1 && (
          <form
            onSubmit={handleSendCode}
            className="space-y-4"
          >
            <div>
              <label className="text-sm text-gray-600">
                Email Address
              </label>

              <input
                type="email"
                value={email}
                onChange={(e) =>
                  setEmail(e.target.value)
                }
                required
                className="w-full mt-1 px-3 py-2 border rounded-lg"
              />
            </div>

            <button
              disabled={loading}
              className="w-full bg-black text-white py-2 rounded-lg"
            >
              {loading
                ? "Sending..."
                : "Send Verification Code"}
            </button>
          </form>
        )}

        {/* STEP 2 */}
        {step === 2 && (
          <form
            onSubmit={handleVerifyCode}
            className="space-y-4"
          >
            <div className="text-sm text-gray-500">
              Verification code sent to
              <div className="font-medium text-gray-900 mt-1">
                {email}
              </div>
            </div>

            <div>
              <label className="text-sm text-gray-600">
                Verification Code
              </label>

              <input
                value={code}
                onChange={(e) =>
                  setCode(e.target.value)
                }
                required
                className="w-full mt-1 px-3 py-2 border rounded-lg"
              />
            </div>

            <button
              disabled={loading}
              className="w-full bg-black text-white py-2 rounded-lg"
            >
              {loading
                ? "Verifying..."
                : "Verify Email"}
            </button>

            <button
              type="button"
              onClick={handleResendCode}
              disabled={loading}
              className="w-full text-sm text-gray-600 hover:text-black"
            >
              Resend Code
            </button>
          </form>
        )}

        {/* STEP 3 */}
        {step === 3 && (
          <form
            onSubmit={handleRegister}
            className="space-y-4"
          >
            <div>
              <label className="text-sm text-gray-600">
                Full Name
              </label>

              <input
                value={fullName}
                onChange={(e) =>
                  setFullName(e.target.value)
                }
                required
                className="w-full mt-1 px-3 py-2 border rounded-lg"
              />
            </div>

            <div>
              <label className="text-sm text-gray-600">
                Password
              </label>

              <input
                type="password"
                value={password}
                onChange={(e) =>
                  setPassword(e.target.value)
                }
                required
                className="w-full mt-1 px-3 py-2 border rounded-lg"
              />
            </div>

            <div>
              <label className="text-sm text-gray-600">
                Confirm Password
              </label>

              <input
                type="password"
                value={password2}
                onChange={(e) =>
                  setPassword2(e.target.value)
                }
                required
                className="w-full mt-1 px-3 py-2 border rounded-lg"
              />
            </div>

            <button
              disabled={loading}
              className="w-full bg-black text-white py-2 rounded-lg"
            >
              {loading
                ? "Creating Account..."
                : "Create Account"}
            </button>
          </form>
        )}

        <div className="mt-8 text-center text-sm text-gray-500">
          Already have an account?{" "}
          <button
            onClick={() => router.push("/login")}
            className="text-black font-medium"
          >
            Sign In
          </button>
        </div>
      </div>
    </div>
  );
}

function Step({
  active,
  children,
}: {
  active: boolean;
  children: React.ReactNode;
}) {
  return (
    <div
      className={`flex-1 text-center text-xs py-2 rounded-md ${
        active
          ? "bg-black text-white"
          : "bg-gray-100 text-gray-500"
      }`}
    >
      {children}
    </div>
  );
}