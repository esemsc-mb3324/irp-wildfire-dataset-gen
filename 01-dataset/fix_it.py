input_file = "input_tracking.txt"
output_file = "input_tracking.txt"

with open(input_file, "r") as f:
    lines = [line.rstrip() for line in f]

fixed_lines = [lines[0]]  # header
for i in range(1, len(lines)-1, 2):
    main = lines[i]
    firearea = lines[i+1].strip()
    fixed_lines.append(f"{main},{firearea}")

with open(output_file, "w") as f:
    for line in fixed_lines:
        f.write(line + "\n")