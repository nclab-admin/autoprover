"""evaluation function for chromosome
"""

import subprocess
from subprocess import PIPE, STDOUT
from evaluation.coqstate import CoqState

def preprocess(theorem, chromosome):
    """
    convert chromosome to complete Coq script
    """
    script = [] + theorem
    script += ["Proof."]
    script += ["intros."]
    script += chromosome
    script += ["Qed."]
    return script

def run_coqtop(script):
    """
    run Coq script and return output
    """
    coqtop = subprocess.Popen('coqtop', shell=False,
                              stdin=PIPE, stdout=PIPE, stderr=STDOUT)

    # truncate to byte string
    byte_string = b''
    for line in script:
        byte_string += line.encode('utf-8')
        byte_string += b'\n'

    # communicate with coqtop
    (out, _) = coqtop.communicate(input=byte_string)

    return out.decode('utf-8')

def get_coq_states(result, proof, chromosome):
    """
    return valid coq states
    """
    splited_result = split_coqtop_result(result, proof.theorem_name)

    filtered_result = []
    tactics_set = set()
    for (i, step) in enumerate(splited_result):
        if i == 0:
            filtered_result.append(CoqState(step))
            continue

        state = CoqState(step)
        if state.is_no_more_goal:
            filtered_result.append(state)
        elif state.is_error_state:
            break
        elif state == filtered_result[-1]:
            break
        elif i > 1 and proof.tactics.is_unrepeatable(chromosome[i-2]):
            if chromosome[i-2] in tactics_set:
                break
            else:
                tactics_set.add(chromosome[i-2])
        else:
            filtered_result.append(state)

    return filtered_result

def evaluate_result(result, theorem_name, error_threshold=0,
                    useless_threshold=0):
    """
    evaluate result from coq, return (is_proved, proof)
    """
    valid_tactic = -1
    error_tactic = 0
    useless_tactic = 0

    total_steps = split_coqtop_result(result, theorem_name)

    for (i, step) in enumerate(total_steps):
        if i == 0:
            valid_tactic += 1
            continue

        if is_no_more_goal(step):
            return (True, valid_tactic)
        if check_prev_step(total_steps, i) is True:
            if is_error_step(step):
                error_tactic += 1
            else:
                valid_tactic += 1
        else:
            useless_tactic += 1
        if error_tactic > error_threshold or useless_tactic > useless_threshold:
            break

    return (False, valid_tactic)

def check_prev_step(total_steps, cur_idx):
    """
    if current step show before return True otherwise False
    """
    for i in range(cur_idx):
        if total_steps[cur_idx] == total_steps[i]:
            return False
    return True

def is_error_step(step):
    """
    check for an error
    """
    for line in step:
        if line.startswith("Error:"):
            return True
    return False

def is_no_more_goal(step):
    """
    check for specific message which means proof completed
    """
    for line in step:
        if line.startswith("Error: No such unproven subgoal"):
            return True
        if line.find("No more subgoals.") > -1:
            return True
    return False

def split_coqtop_result(result, theorem_name):
    """
    split result into steps
    """
    total_steps = []
    step = []
    state = "begin"
    spliter = theorem_name + " <"

    for line in result.split("\n"):
        line = line.strip()
        if state == "begin":
            if line.startswith(spliter):
                state = "start"
                step = [line]
        else:
            if line.startswith(spliter):
                total_steps.append(step)
                step = [line]
            else:
                step.append(line)
    total_steps.append(step)

    return total_steps

def calculate_fitness(coq_states, chromosome, tactics):
    """calculate fitness from coqstates
    score = sum(len(hypothesis)/len(goal))
    """
    score = 0.0
    for index, state in enumerate(coq_states):
        if (index > 2 and chromosome[index-2] == chromosome[index-3]
                and tactics.is_unrepeatable(chromosome[index-2])):
            coq_states = coq_states[:index]
            break
        score += len(state.hypothesis) / len(state.goal)
    return score