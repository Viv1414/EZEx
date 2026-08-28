import { notFound } from "next/navigation";

import { getExercise } from "@/lib/api";
import { getAuthCookieHeader } from "@/lib/server-auth";

export default async function ExercisePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const cookieHeader = await getAuthCookieHeader();
  const exercise = await getExercise(Number(id), cookieHeader);

  if (!exercise) {
    notFound();
  }

  const modifications = [
    { label: "Beginner", text: exercise.modification_beginner },
    { label: "Intermediate", text: exercise.modification_intermediate },
    { label: "Advanced", text: exercise.modification_advanced },
  ].filter((m) => m.text);

  return (
    <main className="mx-auto max-w-2xl px-6 py-16">
      <a href="/dashboard" className="text-sm text-zinc-500 hover:underline">
        &larr; All exercises
      </a>
      <h1 className="mt-2 text-2xl font-semibold text-zinc-900 dark:text-zinc-50">
        {exercise.name}
      </h1>
      <p className="text-sm text-zinc-500">
        {exercise.general_part} / {exercise.body_part}
      </p>

      {exercise.video_url && (
        <video controls className="mt-6 w-full rounded-lg bg-black">
          <source src={exercise.video_url} />
        </video>
      )}

      {exercise.diagram_url && (
        // eslint-disable-next-line @next/next/no-img-element -- external, partner-provided image; no need for next/image's optimization pipeline yet
        <img
          src={exercise.diagram_url}
          alt={`Diagram of the ${exercise.body_part}`}
          className="mt-6 max-h-80 rounded-lg border border-zinc-200 dark:border-zinc-800"
        />
      )}

      {exercise.instructions.length > 0 && (
        <div className="mt-8">
          <h2 className="text-lg font-medium text-zinc-900 dark:text-zinc-50">
            Instructions
          </h2>
          <ol className="mt-3 list-decimal space-y-1 pl-5 text-zinc-700 dark:text-zinc-300">
            {exercise.instructions.map((step, i) => (
              <li key={i}>{step}</li>
            ))}
          </ol>
        </div>
      )}

      {exercise.frequency && (
        <div className="mt-6">
          <h2 className="text-lg font-medium text-zinc-900 dark:text-zinc-50">
            Frequency
          </h2>
          <p className="mt-1 text-zinc-700 dark:text-zinc-300">{exercise.frequency}</p>
        </div>
      )}

      {exercise.equipment.length > 0 && (
        <div className="mt-6">
          <h2 className="text-lg font-medium text-zinc-900 dark:text-zinc-50">
            Equipment needed
          </h2>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-zinc-700 dark:text-zinc-300">
            {exercise.equipment.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
        </div>
      )}

      {exercise.common_mistakes.length > 0 && (
        <div className="mt-6">
          <h2 className="text-lg font-medium text-zinc-900 dark:text-zinc-50">
            Common mistakes
          </h2>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-zinc-700 dark:text-zinc-300">
            {exercise.common_mistakes.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
        </div>
      )}

      {modifications.length > 0 && (
        <div className="mt-6">
          <h2 className="text-lg font-medium text-zinc-900 dark:text-zinc-50">
            Modifications
          </h2>
          <dl className="mt-2 flex flex-col gap-2">
            {modifications.map((m) => (
              <div key={m.label}>
                <dt className="text-sm font-medium text-zinc-500">{m.label}</dt>
                <dd className="text-zinc-700 dark:text-zinc-300">{m.text}</dd>
              </div>
            ))}
          </dl>
        </div>
      )}

      {exercise.injuries.length > 0 && (
        <div className="mt-8">
          <h2 className="text-lg font-medium text-zinc-900 dark:text-zinc-50">
            Helps with
          </h2>
          <ul className="mt-3 flex flex-col gap-2">
            {exercise.injuries.map((injury) => (
              <li
                key={injury.id}
                className="flex items-center justify-between rounded-lg border border-zinc-200 px-4 py-2 dark:border-zinc-800"
              >
                <a href={`/injuries/${injury.id}`} className="capitalize hover:underline">
                  {injury.name}
                </a>
                <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                  {injury.effectiveness}/5
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </main>
  );
}
