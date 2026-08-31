import { getInjuries } from "@/lib/api";
import { getAuthCookieHeader } from "@/lib/server-auth";
import NewProgramForm from "@/components/NewProgramForm";

export default async function NewProgramPage() {
  const cookieHeader = await getAuthCookieHeader();
  const injuries = await getInjuries(cookieHeader);

  return (
    <main className="mx-auto w-full max-w-sm px-6 py-16">
      <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">New Program</h1>
      <NewProgramForm injuries={injuries} />
    </main>
  );
}
