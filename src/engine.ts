import scenario from './scenario.json' with { type: 'json' };
export const WRONG_INPUT = 'WRONG INPUT/CONTRACT MATERIAL - PROVIDE CORRECT VERSION.';
export const TOTAL_SECONDS = scenario.stages.reduce((sum, stage) => sum + stage.duration, 0);
export const taskTimeline = scenario.stages.flatMap((stage, stageIndex) => stage.tasks.map((task, taskIndex) => ({
  ...task, stageIndex, taskIndex,
  start: scenario.stages.slice(0, stageIndex).reduce((sum, s) => sum + s.duration, 0) + taskIndex * stage.duration / stage.tasks.length,
  end: scenario.stages.slice(0, stageIndex).reduce((sum, s) => sum + s.duration, 0) + (taskIndex + 1) * stage.duration / stage.tasks.length,
})));
export type Mode = 'idle' | 'ready' | 'running' | 'paused' | 'review' | 'ended';
export type RunState = { mode: Mode; elapsed: number; hiddenPause: boolean };
export type RunAction = { type: 'ACCEPT' | 'START' | 'PAUSE' | 'RESUME' | 'END' | 'RESET' | 'HIDE' } | { type: 'TICK'; delta: number };
export const initialRun: RunState = { mode: 'idle', elapsed: 0, hiddenPause: false };
export function currentTask(elapsed: number) { return taskTimeline.find(task => task.end > elapsed) || taskTimeline.at(-1)!; }
export function runReducer(state: RunState, action: RunAction): RunState {
  switch (action.type) {
    case 'ACCEPT': return state.mode === 'idle' ? { ...initialRun, mode: 'ready' } : state;
    case 'START': return state.mode === 'ready' ? { ...state, mode: 'running' } : state;
    case 'PAUSE': return state.mode === 'running' ? { ...state, mode: 'paused', hiddenPause: false } : state;
    case 'HIDE': return state.mode === 'running' ? { ...state, mode: 'paused', hiddenPause: true } : state;
    case 'RESUME': return state.mode === 'paused' ? { ...state, mode: 'running', hiddenPause: false } : state;
    case 'END': return state.mode === 'review' ? { ...state, mode: 'ended' } : state;
    case 'RESET': return initialRun;
    case 'TICK': {
      if (state.mode !== 'running' || !Number.isFinite(action.delta) || action.delta <= 0) return state;
      // Never skip a task after throttling or a stalled frame: each new task gets its own reading time.
      const elapsed = Math.min(state.elapsed + action.delta, currentTask(state.elapsed).end, TOTAL_SECONDS);
      return { ...state, elapsed, mode: elapsed >= TOTAL_SECONDS ? 'review' : 'running' };
    }
  }
}
export async function acceptsInput(line: number, file: { size: number; arrayBuffer(): Promise<ArrayBuffer> }, expectedSha256: string): Promise<boolean> {
  if (line !== 1 || file.size === 0 || file.size > 5 * 1024 * 1024) return false;
  try {
    const buffer = await file.arrayBuffer();
    const hash = await crypto.subtle.digest('SHA-256', buffer);
    const hex = Array.from(new Uint8Array(hash), value => value.toString(16).padStart(2, '0')).join('');
    return hex === expectedSha256;
  } catch { return false; }
}
export function formatTime(seconds: number) { const value = Math.floor(seconds); return `${Math.floor(value / 60)}:${String(value % 60).padStart(2, '0')}`; }
