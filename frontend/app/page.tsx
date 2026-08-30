export default function Home() {
  return (
    <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col items-center justify-center px-6 py-16 text-center">
      <h1 className="text-3xl font-semibold text-zinc-900 dark:text-zinc-50">ezex</h1>
      <p className="mt-2 text-zinc-500">Physiotherapy made easy.</p>
      <a
        href="/signup"
        className="mt-8 rounded-full bg-zinc-900 px-6 py-3 text-sm font-medium text-white hover:bg-zinc-800 dark:bg-zinc-50 dark:text-zinc-900 dark:hover:bg-zinc-200"
      >
        Get started for free
      </a>
    </main>
  );
}
