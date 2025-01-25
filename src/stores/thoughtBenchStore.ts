import { reactive } from "vue";
import type { ThoughtBenchColumnData, ThoughtBenchColumnState } from "../types";

function loadDefaultState() {
    return {
        dataColumns: [
            {
                model: "ollama:deepseek-r1:1.5b",
                totalCorrect: 0,
                responses: [],
                state: "idle" as ThoughtBenchColumnState
            },
            {
                model: "ollama:deepseek-r1:8b",
                totalCorrect: 0,
                responses: [],
                state: "idle" as ThoughtBenchColumnState
            },
            {
                model: "ollama:deepseek-r1:14b", 
                totalCorrect: 0,
                responses: [],
                state: "idle" as ThoughtBenchColumnState
            },
            {
                model: "ollama:deepseek-r1:32b",
                totalCorrect: 0,
                responses: [],
                state: "idle" as ThoughtBenchColumnState
            },
            {
                model: "ollama:deepseek-r1:70b",
                totalCorrect: 0,
                responses: [],
                state: "idle" as ThoughtBenchColumnState
            },
            {
                model: "deepseek:deepseek-reasoner",
                totalCorrect: 0,
                responses: [],
                state: "idle" as ThoughtBenchColumnState
            }
        ] as ThoughtBenchColumnData[],
        prompt: "",
        totalExecutions: 0,
        apiCallInProgress: false,
        settings: {
            modelStatDetail: 'verbose' as 'verbose' | 'hide',
            columnWidth: 400
        }
    };
}

function loadState() {
    const savedState = localStorage.getItem('thoughtBenchState');
    if (savedState) {
        try {
            return JSON.parse(savedState);
        } catch (e) {
            console.error('Failed to parse saved state:', e);
            return loadDefaultState();
        }
    }
    return loadDefaultState();
}

export function resetState() {
    const defaultState = loadDefaultState();
    setState(defaultState);
    localStorage.setItem('thoughtBenchState', JSON.stringify(store));
}

function setState(state: any) {
    store.dataColumns = state.dataColumns;
    store.prompt = state.prompt;
    store.totalExecutions = state.totalExecutions;
    store.apiCallInProgress = state.apiCallInProgress;
    store.settings = state.settings;
}

export const store = reactive(loadState());
