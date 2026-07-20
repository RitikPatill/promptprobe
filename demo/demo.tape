Output demo/demo.gif

Require vhs

Set Shell "bash"
Set FontSize 14
Set Width 1000
Set Height 550
Set Theme "Dracula"

Type "# PromptProbe — prompt regression testing demo" Sleep 500ms Enter
Sleep 1s

Type "cat examples/qa_suite.yaml" Sleep 300ms Enter
Sleep 2s

Type "promptprobe list demo" Sleep 300ms Enter
Sleep 1s

Type "promptprobe eval examples/qa_suite.yaml" Sleep 300ms Enter
Sleep 4s

Type "promptprobe diff demo/run_a.json demo/run_b.json" Sleep 300ms Enter
Sleep 3s
