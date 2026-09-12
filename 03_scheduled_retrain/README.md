# Scheduled training

> "Last Tuesday’s model is the current best. What config produced it, and can I re-run it with a single thing changed?"

This example exercises:

- `Config` as a declarative training configuration
- `cascade run` overrides and configuration capture
- captured run logs and saved config files
- `ModelLine` for the history of models
- Reruns from a previous model configuration with `--base`

## Run this example

Run the tracked job from its directory:

```bash
cascade run train.py -y --log
```

Override the feature window:

```bash
cascade run train.py -y --log --window_days 14
```

To inherit a prior run, first find its slug, then use that line entry as the
base for the next run:

```bash
cd line
cascade query slug metrics[0].value
cd ..
cascade run train.py -y --log --base line/<slug> --l2 0.01
```

`add_config()` and `add_log()` will work only inside `cascade run` and not if you run the script directly

## See the results

List the saved models and their metrics:

```bash
cd line
cascade query slug 'metrics[0].name' 'metrics[0].value' params.l2 params.window_days sort metrics[0].value desc
```

For each tracked run you can inspect `line/<model>/files/` for
`cascade_config.json`, `cascade_overrides.json`, and `cascade_run.log`.

## Learn more

- [Configuration management and reruns](https://oxid15.github.io/cascade/en/latest/tutorials/configuration_management.html)
- [Using the Cascade CLI](https://oxid15.github.io/cascade/en/latest/howtos/cli.html)
- [Model lines and repositories](https://oxid15.github.io/cascade/en/latest/explanations/model.html)
