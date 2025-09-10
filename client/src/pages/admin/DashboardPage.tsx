import { useSuperAdmin } from "@/hooks/useSuperAdmin";
import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export default function AdminDashboardPage() {
  const { userList, isUserListLoading, createNewUser } = useSuperAdmin();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) return;
    try {
      setSubmitting(true);
      await createNewUser(email, password);
      setEmail("");
      setPassword("");
    } finally {
      setSubmitting(false);
    }
  };

  if (isUserListLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold text-gray-900">Admin Dashboard</h1>
      <p className="text-gray-600">Welcome to the admin dashboard.</p>
      <div className="bg-white rounded-lg shadow p-4">
        <h2 className="text-lg font-semibold mb-3">Create New User</h2>
        <form onSubmit={onSubmit} className="grid grid-cols-1 md:grid-cols-3 gap-3 items-end">
          <div>
            <label className="block text-sm text-gray-700 mb-1">Email</label>
            <Input
              type="email"
              placeholder="user@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="block text-sm text-gray-700 mb-1">Password</label>
            <Input
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <div>
            <Button type="submit" disabled={submitting}>
              {submitting ? "Creating..." : "Create User"}
            </Button>
          </div>
        </form>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {userList?.users.map((user) => (
          <div key={user.id} className="bg-white p-4 rounded-lg shadow-md">
            <h2 className="text-lg font-semibold text-gray-900">{user.email}</h2>
            <p className="text-gray-600">{user.role}</p>
          </div>
        ))}
      </div>
    </div>
  );
}


