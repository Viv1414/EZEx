import { notFound } from "next/navigation";

import { getProgram } from "@/lib/api";
import { getAuthCookieHeader } from "@/lib/server-auth";
import ProgramDetailView from "@/components/ProgramDetailView";

export default async function ProgramPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const cookieHeader = await getAuthCookieHeader();
  const program = await getProgram(Number(id), cookieHeader);

  if (!program) {
    notFound();
  }

  return (
    <main className="mx-auto max-w-2xl px-6 py-16">
      <a href="/dashboard" className="text-sm text-zinc-500 hover:underline">
        &larr; All exercises
      </a>
      <ProgramDetailView program={program} />
    </main>
  );
}
