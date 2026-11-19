[
    ("aging measured from time 0 instead of from arrival", "(ij[1][2] + (t - ij[1][1]) // aging, -ij[1][1], -ij[0])", "(ij[1][2] + t // aging, -ij[1][1], -ij[0])"),
    ("idle worker wakes one unit after the next arrival", "            t = min(j[1] for _, j in pending)  # idle until the next arrival", "            t = min(j[1] for _, j in pending) + 1"),
    ("equal effective priority goes to the job listed last", "(ij[1][2] + (t - ij[1][1]) // aging, -ij[1][1], -ij[0])", "(ij[1][2] + (t - ij[1][1]) // aging, -ij[1][1], ij[0])"),
]
