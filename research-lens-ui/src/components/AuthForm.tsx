import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface AuthFormProps {
  onLogin: (username: string) => void;
}

// Demo credentials
const DEMO_USERS = {
  demo: "demo123",
  admin: "admin123",
  test: "test123"
};

export function AuthForm({ onLogin }: AuthFormProps) {
  const [loginUsername, setLoginUsername] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [signupUsername, setSignupUsername] = useState("");
  const [signupPassword, setSignupPassword] = useState("");
  const [signupConfirm, setSignupConfirm] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!loginUsername || !loginPassword) {
      setError("Please fill in all fields");
      return;
    }

    // Check demo credentials
    if (DEMO_USERS[loginUsername as keyof typeof DEMO_USERS] === loginPassword) {
      onLogin(loginUsername);
    } else {
      setError("Invalid username or password");
    }
  };

  const handleSignup = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (!signupUsername || !signupPassword || !signupConfirm) {
      setError("Please fill in all fields");
      return;
    }

    if (signupPassword !== signupConfirm) {
      setError("Passwords do not match");
      return;
    }

    if (signupPassword.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    // In a real app, this would create an account
    // For demo, just show success and suggest using demo credentials
    setSuccess("Account created! Use demo credentials to login: demo/demo123");
    setSignupUsername("");
    setSignupPassword("");
    setSignupConfirm("");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold">ResearchLens</CardTitle>
          <CardDescription>AI-Powered Research Analysis</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="login" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="login">Login</TabsTrigger>
              <TabsTrigger value="signup">Sign Up</TabsTrigger>
            </TabsList>

            {/* Login Tab */}
            <TabsContent value="login">
              <form onSubmit={handleLogin} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="login-username">Username</Label>
                  <Input
                    id="login-username"
                    type="text"
                    placeholder="Enter username"
                    value={loginUsername}
                    onChange={(e) => setLoginUsername(e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="login-password">Password</Label>
                  <Input
                    id="login-password"
                    type="password"
                    placeholder="Enter password"
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                  />
                </div>

                {error && (
                  <Alert variant="destructive">
                    <AlertDescription className="text-sm">{error}</AlertDescription>
                  </Alert>
                )}

                <Button type="submit" className="w-full">
                  Login
                </Button>

                <Alert className="bg-muted">
                  <AlertDescription className="text-xs">
                    <strong className="block mb-1">Demo Credentials:</strong>
                    <div className="space-y-0.5 text-muted-foreground">
                      <div>Username: <code className="font-mono">demo</code></div>
                      <div>Password: <code className="font-mono">demo123</code></div>
                    </div>
                  </AlertDescription>
                </Alert>
              </form>
            </TabsContent>

            {/* Signup Tab */}
            <TabsContent value="signup">
              <form onSubmit={handleSignup} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="signup-username">Username</Label>
                  <Input
                    id="signup-username"
                    type="text"
                    placeholder="Choose username"
                    value={signupUsername}
                    onChange={(e) => setSignupUsername(e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="signup-password">Password</Label>
                  <Input
                    id="signup-password"
                    type="password"
                    placeholder="Choose password (min 6 chars)"
                    value={signupPassword}
                    onChange={(e) => setSignupPassword(e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="signup-confirm">Confirm Password</Label>
                  <Input
                    id="signup-confirm"
                    type="password"
                    placeholder="Confirm password"
                    value={signupConfirm}
                    onChange={(e) => setSignupConfirm(e.target.value)}
                  />
                </div>

                {error && (
                  <Alert variant="destructive">
                    <AlertDescription className="text-sm">{error}</AlertDescription>
                  </Alert>
                )}

                {success && (
                  <Alert className="bg-green-50 border-green-200">
                    <AlertDescription className="text-sm text-green-800">
                      {success}
                    </AlertDescription>
                  </Alert>
                )}

                <Button type="submit" className="w-full">
                  Sign Up
                </Button>

                <Alert className="bg-muted">
                  <AlertDescription className="text-xs text-muted-foreground">
                    This is a demo app. Use demo credentials to access features.
                  </AlertDescription>
                </Alert>
              </form>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}
