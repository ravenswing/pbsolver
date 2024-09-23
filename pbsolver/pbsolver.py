import click
import MDAnalysis as mda
import MDAnalysis.transformations as trans
from pathlib import Path

@click.command()
@click.argument(
    "topology",
    type=click.Path(
        exists=True,
        file_okay=True,
        readable=True,
        path_type=Path,
    ),
)
@click.argument(
    "trajectory",
    type=click.Path(
        exists=True,
        file_okay=True,
        readable=True,
        path_type=Path,
    ),
)
@click.option('-o', '--output')
@click.option('-s', '--select')
@click.option('-a', '--align-to')
@click.option('--align-select')
def cli(topology, trajectory, output, select, align_to):
    click.echo(click.style(topology, fg='green'))

    # Initialise the file as a universe
    u = mda.Universe(topology, trajectory)

    if output is None:
       output = trajectory
    elif "/" not in output:
        output = trajectory.parent / Path(output)
    else:
        output = Path(output)

    protein = u.select_atoms('protein')
    not_protein = u.select_atoms('not protein')

    transforms = [trans.unwrap(protein),
                  trans.center_in_box(protein, wrap=True),
                  trans.wrap(not_protein)]

    u.trajectory.add_transformations(*transforms)

    out_group = u.select_atoms(select) if select else u.atoms

    #if indices is None:
    with mda.Writer(str(output), out_group.n_atoms) as W:
        with click.progressbar(u.trajectory,
                               label='Processing trajectory frames',
                               length=u.trajectory.n_frames) as bar:
            for ts in bar:
                W.write(out_group)

    if align_to is not None:
        mobile = mda.Universe(topology, output)
        reference = mda.Universe(align_to)

        align_selection = "backbone" if align_select is None else align_select

        aligner = align.AlignTraj(mobile, reference, select=selection, filename=str(output))
        aligner.run()

    # else:
        # with mda.Writer(out_path, out_group.n_atoms) as W:
            # for idx in indices:
                # u.trajectory[idx]
                # W.write(out_group)


def main():
    cli()

if __name__ == "__main__":
    main()
