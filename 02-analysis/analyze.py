"""Reproduce published aggregate rates, or analyze a supplied anonymized survey CSV.

No individual responses are synthesized. Python 3 standard library only.
Examples:
  python analyze.py
  python analyze.py --responses ../01-research/responses-template.csv
"""
import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def published_summary():
    with (ROOT / 'public-study.csv').open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    result = []
    for row in rows:
        yes, n = int(row['yes_count']), int(row['sample_size'])
        if not 0 <= yes <= n or n <= 0:
            raise ValueError('Invalid numerator or denominator')
        rate = yes / n
        result.append({
            'metric': row['metric'], 'yes_count': yes, 'sample_size': n,
            'calculated_percent': round(100 * rate, 2),
            'published_rounded_percent': int(row['published_percent']),
            'source_doi': row['source_doi'],
        })
    with (ROOT / 'public-study-verified.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(result[0]))
        writer.writeheader()
        writer.writerows(result)
    print(json.dumps({'data_type': 'published_aggregate_not_project_survey',
                      'results': result}, ensure_ascii=False, indent=2))


def analyze_responses(source):
    """Complete-case, unique-ID analysis. Missing values are excluded, not zero."""
    with source.open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    if not rows:
        print('No project responses supplied. No project statistics generated.')
        return
    required = {'response_id', 'city', 'duration_seconds', 'adoption_intent',
                'has_pet_experience', 'consent'}
    if not required <= rows[0].keys():
        raise ValueError('Missing columns: ' + ','.join(sorted(required - rows[0].keys())))
    seen, kept, excluded = set(), [], Counter()
    for row in rows:
        response_id = row['response_id'].strip()
        if not response_id or response_id in seen:
            excluded['missing_or_duplicate_id'] += 1
            continue
        seen.add(response_id)
        if row['consent'].strip() != 'yes':
            excluded['no_consent'] += 1
            continue
        try:
            duration = float(row['duration_seconds'])
        except ValueError:
            excluded['invalid_duration'] += 1
            continue
        # Duration is recorded but no arbitrary time cutoff is imposed.
        if duration < 0:
            excluded['invalid_duration'] += 1
            continue
        if row['adoption_intent'] not in {'yes', 'no', 'unsure'}:
            excluded['missing_or_invalid_adoption_intent'] += 1
            continue
        kept.append(row)
    descriptions = Counter(r['adoption_intent'] for r in kept)
    cross = defaultdict(Counter)
    for row in kept:
        if row['has_pet_experience'] in {'yes', 'no'}:
            cross[row['has_pet_experience']][row['adoption_intent']] += 1
    cross_rows = []
    for experience, counts in sorted(cross.items()):
        n = sum(counts.values())
        for intent in ('yes', 'no', 'unsure'):
            cross_rows.append({'has_pet_experience': experience,
                              'adoption_intent': intent, 'count': counts[intent],
                              'group_n': n, 'within_group_percent': round(100 * counts[intent] / n, 2)})
    report = {'source_file': source.name, 'input_n': len(rows), 'retained_n': len(kept),
              'excluded_by_reason': dict(excluded),
              'adoption_intent_counts': dict(descriptions),
              'cross_tab_pet_experience_by_adoption_intent': cross_rows}
    (ROOT / 'project-survey-results.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--responses', type=Path)
    args = parser.parse_args()
    if args.responses:
        analyze_responses(args.responses)
    else:
        published_summary()
