"use client";

import ProtectedRoute from "@/lib/auth/ProtectedRoute";
import { useAuthContext } from "@/lib/auth/auth-provider";
import { useRouter } from "next/navigation";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { logout } = useAuthContext();
  const router = useRouter();

  return (
    <ProtectedRoute>
      <div className="min-h-screen flex bg-gray-50">
        
        {/* Sidebar */}
        <aside className="w-64 bg-white border-r p-4">
          <h2 className="font-semibold text-lg">YNX</h2>

          <nav className="mt-6 space-y-2 text-sm">
            <button className="block w-full text-left px-2 py-1 rounded hover:bg-gray-100">
              Automations
            </button>

            <button className="block w-full text-left px-2 py-1 rounded hover:bg-gray-100">
              Executions
            </button>
          </nav>

          <button
            onClick={() => {
              logout();
              router.push("/login");
            }}
            className="mt-10 text-sm text-red-500"
          >
            Logout
          </button>
        </aside>

        {/* Main content */}
        <main className="flex-1 p-6">
          {children}
        </main>

      </div>
    </ProtectedRoute>
  );
}