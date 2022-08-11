from cwdb import Cell, CWComplex
from tts import TaskTypeSystem


def main():
    cw = CWComplex()
    tts = TaskTypeSystem(cw)

    def printer(n: Cell) -> None:
        assert tts.is_instance_of(n, tts.Int)
        arg_value = int(n.label)
        for _ in range(arg_value):
            print("Hello world!")

    hw = tts.create_task("hello_world_n_times", {"n": tts.Int}, code=printer)
    arg_value_cell = cw.create_cell("7")
    cw.link(arg_value_cell, tts.Int, "io")

    tts.eval_task(hw, {"n": arg_value_cell})


if __name__ == "__main__":
    main()
