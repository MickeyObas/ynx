import { api } from "../api-client";

export const sendVerificationCode = async (email: string) => {
  const res = await api.post("auth/send-confirmation-code/", {
    email,
  });

  return res.data;
};

export const resendVerificationCode = async (email: string) => {
  const res = await api.post("auth/resend-confirmation-code/", {
    email,
  });

  return res.data;
};

export const verifyEmail = async (
  code: string,
  token: string
) => {
  const res = await api.post("auth/verify-email/", {
    code,
    token,
  });

  return res.data;
};

export const registerUser = async (data: {
  email: string;
  full_name: string;
  password: string;
  password2: string;
}) => {
  const res = await api.post("auth/register/", data);
  return res.data;
};