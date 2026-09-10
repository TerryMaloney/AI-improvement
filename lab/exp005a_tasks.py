"""Deterministic closed-world task generation for EXP005A.

No model, web access, or evaluator is used to create ground truth. Every task key
is computed by the same finite procedure that generates the instance. Discovery
items are identified by (family, seed); a later freeze record can fingerprint the
serialized bank.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import random
import re
from typing import Iterable

FAMILIES = ("arithmetic", "ordering", "state_machine", "multihop")


@dataclass(frozen=True)
class Exp005Task:
    task_id: str
    family: str
    seed: int
    prompt: str
    answer: str
    metadata: dict

    def canonical(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))

    def fingerprint(self) -> str:
        return hashlib.sha256(self.canonical().encode()).hexdigest()[:16]


def _rng(family: str, seed: int) -> random.Random:
    h = hashlib.sha256(f"exp005a:{family}:{seed}".encode()).digest()
    return random.Random(int.from_bytes(h[:8], "big"))


def _token(prefix: str, n: int) -> str:
    return f"{prefix}{n:02d}"


def arithmetic_task(seed: int) -> Exp005Task:
    r = _rng("arithmetic", seed)
    start = r.randint(37, 143)
    crates = r.randint(3, 8)
    per_crate = r.randint(4, 13)
    sold = r.randint(11, 47)
    damaged = r.randint(2, 12)
    bonus_groups = r.randint(2, 6)
    bonus_each = r.randint(3, 9)
    answer = start + crates * per_crate - sold - damaged + bonus_groups * bonus_each
    prompt = (
        "A depot begins with {start} sealed units. It receives {crates} crates with "
        "{per_crate} units in each crate, ships {sold} units, discards {damaged} damaged "
        "units, then receives {bonus_groups} small bundles with {bonus_each} units each. "
        "How many sealed units remain? Give only the integer after `FINAL:`."
    ).format(start=start, crates=crates, per_crate=per_crate, sold=sold,
             damaged=damaged, bonus_groups=bonus_groups, bonus_each=bonus_each)
    return Exp005Task(
        task_id=f"arith-{seed:06d}", family="arithmetic", seed=seed,
        prompt=prompt, answer=str(answer),
        metadata={"start": start, "crates": crates, "per_crate": per_crate,
                  "sold": sold, "damaged": damaged,
                  "bonus_groups": bonus_groups, "bonus_each": bonus_each},
    )


def ordering_task(seed: int) -> Exp005Task:
    r = _rng("ordering", seed)
    names = [_token("K", i) for i in r.sample(range(10, 90), 6)]
    order = names[:]
    r.shuffle(order)
    clues = [f"{order[i]} is earlier than {order[i+1]}." for i in range(5)]
    r.shuffle(clues)
    position = r.randint(2, 5)
    answer = order[position - 1]
    prompt = (
        "Six tokens have one strict earliest-to-latest order. The following statements "
        "are all true:\n- " + "\n- ".join(clues) +
        f"\nWhich token is position {position} from the earliest? "
        "End with `FINAL: <token>`."
    )
    return Exp005Task(
        task_id=f"order-{seed:06d}", family="ordering", seed=seed,
        prompt=prompt, answer=answer,
        metadata={"order": order, "position": position, "clues": clues},
    )


def state_machine_task(seed: int) -> Exp005Task:
    r = _rng("state_machine", seed)
    states = [_token("S", i) for i in r.sample(range(10, 90), 5)]
    symbols = ["A", "B", "C"]
    transitions = {}
    for s in states:
        for sym in symbols:
            transitions[(s, sym)] = r.choice(states)
    start = r.choice(states)
    sequence = [r.choice(symbols) for _ in range(r.randint(7, 10))]
    cur = start
    for sym in sequence:
        cur = transitions[(cur, sym)]
    rows = []
    for s in states:
        rows.append(f"{s}: " + ", ".join(f"{sym}->{transitions[(s,sym)]}" for sym in symbols))
    prompt = (
        "A deterministic machine uses these transition rules:\n" + "\n".join(rows) +
        f"\nStart in {start}. Process this input sequence from left to right: " +
        " ".join(sequence) +
        "\nWhat is the final state? End with `FINAL: <state>`."
    )
    return Exp005Task(
        task_id=f"state-{seed:06d}", family="state_machine", seed=seed,
        prompt=prompt, answer=cur,
        metadata={"states": states, "symbols": symbols, "start": start,
                  "sequence": sequence,
                  "transitions": {f"{s}|{sym}": t for (s, sym), t in transitions.items()}},
    )


def multihop_task(seed: int) -> Exp005Task:
    r = _rng("multihop", seed)
    entities = [_token("P", i) for i in r.sample(range(10, 99), 8)]
    chain_len = r.randint(4, 6)
    chain = entities[:chain_len + 1]
    relation = r.choice(["vouches-for", "passes-to", "reports-to"])
    facts = [f"{chain[i]} {relation} {chain[i+1]}." for i in range(chain_len)]
    distractors = []
    remaining = entities[chain_len + 1:]
    if len(remaining) >= 2:
        distractors.append(f"{remaining[0]} admires {remaining[1]}.")
    distractors.append(f"{chain[-1]} admires {chain[0]}.")
    all_facts = facts + distractors
    r.shuffle(all_facts)
    hops = r.randint(2, chain_len)
    answer = chain[hops]
    prompt = (
        "Use only the facts below. Treat each relation as directed and do not use outside "
        "knowledge.\n- " + "\n- ".join(all_facts) +
        f"\nStarting at {chain[0]} and following `{relation}` exactly {hops} times, "
        "which entity do you reach? End with `FINAL: <entity>`."
    )
    return Exp005Task(
        task_id=f"hop-{seed:06d}", family="multihop", seed=seed,
        prompt=prompt, answer=answer,
        metadata={"chain": chain, "relation": relation, "hops": hops,
                  "facts": all_facts},
    )


_GENERATORS = {
    "arithmetic": arithmetic_task,
    "ordering": ordering_task,
    "state_machine": state_machine_task,
    "multihop": multihop_task,
}


def generate_task(family: str, seed: int) -> Exp005Task:
    try:
        return _GENERATORS[family](seed)
    except KeyError as e:
        raise ValueError(f"unknown family {family!r}") from e


def generate_bank(root_seed: int, per_family: int = 12) -> list[Exp005Task]:
    if per_family <= 0:
        raise ValueError("per_family must be positive")
    tasks = []
    for fi, family in enumerate(FAMILIES):
        base = root_seed + fi * 100_000
        tasks.extend(generate_task(family, base + j) for j in range(per_family))
    ids = [t.task_id for t in tasks]
    if len(ids) != len(set(ids)):
        raise AssertionError("duplicate task ids")
    prompts = [t.prompt for t in tasks]
    if len(prompts) != len(set(prompts)):
        raise AssertionError("duplicate prompts")
    return tasks


def bank_fingerprint(tasks: Iterable[Exp005Task]) -> str:
    payload = "\n".join(sorted(t.canonical() for t in tasks))
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


_FINAL_RE = re.compile(r"(?im)^\s*FINAL\s*:\s*(.+?)\s*$")


def extract_final(text: str) -> str | None:
    matches = _FINAL_RE.findall(text or "")
    if not matches:
        return None
    return matches[-1].strip().strip("`* ")


def grade(task: Exp005Task, response: str) -> bool:
    final = extract_final(response)
    if final is None:
        return False
    if task.family == "arithmetic":
        try:
            return int(final.replace(",", "")) == int(task.answer)
        except ValueError:
            return False
    return final.casefold() == task.answer.casefold()
