import { getExercisesByGeneralPart } from "@/lib/api";
import { getAuthCookieHeader } from "@/lib/server-auth";

export default async function CollectionPage({
  params,
}: {
  params: Promise<{ part: string }>;
}) {
  const { part } = await params;
  const generalPart = decodeURIComponent(part);
  const cookieHeader = await getAuthCookieHeader();
  const exercises = await getExercisesByGeneralPart(generalPart, cookieHeader);

  return (
    <main className="mx-auto max-w-2xl px-6 py-16">
      <a href="/dashboard" className="text-sm text-zinc-500 hover:underline">
        &larr; All exercises
      </a>
      <h1 className="mt-2 text-2xl font-semibold capitalize text-zinc-900 dark:text-zinc-50">
        {generalPart}
      </h1>

      {exercises.length === 0 ? (
        <p className="mt-4 text-zinc-500">No exercises in this collection yet.</p>
      ) : (
        <ul className="mt-6 flex flex-col gap-4">
          {exercises.map((exercise) => (
            <li key={exercise.id}>
              <a
                href={`/exercises/${exercise.id}`}
                className="block rounded-lg border border-zinc-200 p-4 hover:bg-zinc-50 dark:border-zinc-800 dark:hover:bg-zinc-900"
              >
                <h2 className="font-medium text-zinc-900 dark:text-zinc-50">
                  {exercise.name}
                </h2>
                <p className="text-sm text-zinc-500">
                  {exercise.general_part} / {exercise.body_part}
                </p>
              </a>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
