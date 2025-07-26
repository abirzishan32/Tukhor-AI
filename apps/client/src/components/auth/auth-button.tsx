import Link from "next/link";
import { Button } from "@/components/ui/button";
import { getUser } from "@/actions/auth";
import { LogoutButton } from "./logout-button";

interface AuthButtonProps {
  dashboard?: boolean;
}

export async function AuthButton({
  dashboard = false,
}: AuthButtonProps) {

 const user = await getUser();

  return user ? (
    <div className="flex items-center gap-4">
      Hey, {user.profile?.userName || user.email }!
      {dashboard ? (
        <Button asChild size="sm" variant={"default"}>
          <Link href="/dashboard">Dashboard</Link>
        </Button>
      ) : null}
      <LogoutButton />
    </div>
  ) : (
    <div className="flex gap-2">
      <Button asChild size="sm" variant={"outline"}>
        <Link href="/auth/login">Sign in</Link>
      </Button>
      <Button asChild size="sm" variant={"default"}>
        <Link href="/auth/sign-up">Sign up</Link>
      </Button>
    </div>
  );
}
