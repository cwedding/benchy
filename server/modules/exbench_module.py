from typing import List
from modules.data_types import (
    ExecEvalBenchmarkFile,
    ExecEvalBenchmarkCompleteResult,
    ExeEvalBenchmarkOutputResult,
    ExecEvalBenchmarkModelReport,
    ExecEvalBenchmarkReport,
    ModelAlias,
    ExeEvalType,
    ModelProvider,
)
from modules.ollama_llm import bench_prompt
from modules.execution_evaluators import (
    execute_python_code_with_num_output,
    eval_result_compare,
)
from utils import parse_markdown_backticks


def run_benchmark_for_model(
    model: str, benchmark_file: ExecEvalBenchmarkFile
) -> List[ExeEvalBenchmarkOutputResult]:
    results = []
    total_tests = len(benchmark_file.prompts)

    for i, prompt_row in enumerate(benchmark_file.prompts, 1):
        print(f"  Running test {i}/{total_tests}...")

        # Replace dynamic variables in base prompt
        prompt = benchmark_file.base_prompt
        if prompt_row.dynamic_variables:
            for key, value in prompt_row.dynamic_variables.items():
                prompt = prompt.replace(f"{{{{{key}}}}}", str(value))

        if benchmark_file.model_provider == ModelProvider.ollama.value:
            # Get benchmark response
            bench_response = bench_prompt(prompt, model)
        elif benchmark_file.model_provider == ModelProvider.mlx.value:
            raise ValueError(
                f"Mlx is not supported yet. Unsupported model provider: {benchmark_file.model_provider}"
            )
        else:
            raise ValueError(
                f"Unsupported model provider: {benchmark_file.model_provider}"
            )

        # Parse and execute the response
        cleaned_code = parse_markdown_backticks(bench_response.response)
        execution_result = ""
        expected_result = str(prompt_row.expectation).strip()  # Get expected result
        try:
            if (
                benchmark_file.evaluator
                == ExeEvalType.execute_python_code_with_num_output
            ):
                execution_result = execute_python_code_with_num_output(cleaned_code)
                parsed_execution_result = str(execution_result).strip()
                correct = eval_result_compare(
                    benchmark_file.evaluator, expected_result, parsed_execution_result
                )
            else:
                raise ValueError(f"Unsupported evaluator: {benchmark_file.evaluator}")
        except Exception as e:
            print("Error executing code:", e)
            execution_result = str(e)
            correct = False

        # Store results
        results.append(
            ExeEvalBenchmarkOutputResult(
                input_prompt=prompt,
                prompt_response=bench_response,
                execution_result=execution_result,
                expected_result=expected_result,  # Add expected result
                model=model,
                correct=correct,
                index=i,  # Add the index
            )
        )
    return results


def generate_report(
    complete_result: ExecEvalBenchmarkCompleteResult,
) -> ExecEvalBenchmarkReport:
    model_reports = []

    # Group results by model
    model_results = {}
    for result in complete_result.results:
        if result.model not in model_results:
            model_results[result.model] = []
        model_results[result.model].append(result)

    # Create model reports
    for model, results in model_results.items():
        correct_count = sum(1 for r in results if r.correct)
        incorrect_count = len(results) - correct_count
        accuracy = correct_count / len(results)

        avg_tokens_per_second = sum(
            r.prompt_response.tokens_per_second for r in results
        ) / len(results)
        avg_total_duration = sum(
            r.prompt_response.total_duration_ms for r in results
        ) / len(results)
        avg_load_duration = sum(
            r.prompt_response.load_duration_ms for r in results
        ) / len(results)

        model_reports.append(
            ExecEvalBenchmarkModelReport(
                model=model,
                results=results,
                correct_count=correct_count,
                incorrect_count=incorrect_count,
                accuracy=accuracy,
                average_tokens_per_second=avg_tokens_per_second,
                average_total_duration_ms=avg_total_duration,
                average_load_duration_ms=avg_load_duration,
            )
        )

    # Calculate overall statistics
    overall_correct = sum(r.correct_count for r in model_reports)
    overall_incorrect = sum(r.incorrect_count for r in model_reports)
    overall_accuracy = overall_correct / (overall_correct + overall_incorrect)

    avg_tokens_per_second = sum(
        r.average_tokens_per_second for r in model_reports
    ) / len(model_reports)
    avg_total_duration = sum(r.average_total_duration_ms for r in model_reports) / len(
        model_reports
    )
    avg_load_duration = sum(r.average_load_duration_ms for r in model_reports) / len(
        model_reports
    )

    return ExecEvalBenchmarkReport(
        benchmark_name=complete_result.benchmark_file.benchmark_name,
        purpose=complete_result.benchmark_file.purpose,
        models=model_reports,
        overall_correct_count=overall_correct,
        overall_incorrect_count=overall_incorrect,
        overall_accuracy=overall_accuracy,
        average_tokens_per_second=avg_tokens_per_second,
        average_total_duration_ms=avg_total_duration,
        average_load_duration_ms=avg_load_duration,
    ).model_dump()