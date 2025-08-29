from app.lambda_invoker import create_lambda_invoker

def produce_report(obj_validation_result : dict[str, any]):

    with open('informe.txt', 'w', encoding='utf-8') as f:
                
        for result in obj_validation_result['results']:
            response_lines = result['execution']['response'].split('\n')
            f.write(f"\nInicio del prompt: {result['prompt_id']}\n")
            for line in response_lines:
                if line.strip():
                    f.write(f"{line}\n")
                else:
                    f.write("\n")
            f.write(f"Fin del informe >>>> {result['execution']['prompt_id']}\n")

def gather_prompt_results(obj_validation_result : dict[str, any]) -> str :

    results_gathered = ''

    for result in obj_validation_result['results']:

        results_gathered += result['execution']['response']

    return results_gathered

def report_to_lambda(report_prompt : str, repo_url: str):

    lambda_invoker = create_lambda_invoker()

    print(f"REPORTE CON OPUS >>>>>>>>>> {report_prompt}")

    lambda_invoker.generate_report(report_prompt, repo_url)