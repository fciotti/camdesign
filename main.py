import argparse
from travel import Travel
from cam import Cam
from follower import Follower
import matplotlib.pyplot as plt
import fileio
import simulation
import numpy as np
from utils import HandledValueError, plot_polar


class ArgumentError(Exception):
    pass


# Overriding ArgumentParser error handling
class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentError(self, message)

    # Do not exit after printing help
    def exit(self, status=0, message=None):
        if message:
            self._print_message(message)
        self.error(None)

interp = ['spline', 'linear', 'harmonic', 'cycloidal', 'parabolic', 'polynomial']
targets = ['travel', 'cam', 'conj']

parser = ArgumentParser(description='camdesign', prog='', add_help=False)
subparsers = parser.add_subparsers(dest='command')
subparsers.required = True

parser_help = subparsers.add_parser('help', help='show this help message')
parser_exit = subparsers.add_parser('exit')

parent_travel = ArgumentParser(add_help=False)
parent_travel.add_argument('--kind', '-k', choices=interp, help='kind of interpolation')
parent_travel.add_argument('--order', '-o', type=int, help='spline/polynomial order')
parent_travel.add_argument('-n', type=int, help='repetitions per cycle')
parent_travel.add_argument('--steps', '-s', type=int, help='interpolation steps')

parent_cam = ArgumentParser(add_help=False)
parent_cam.add_argument('--radius', '-r', type=float, help='base radius')
parent_cam.add_argument('--ccw', action='store_const', const=True, help='counterclockwise')
parent_cam.add_argument('--cw', dest='ccw', action='store_const', const=False, help='clockwise')
parent_cam.add_argument('--follower', '-f', choices=['knife', 'roller', 'flat'], help='follower type')
parent_cam.add_argument('--offset', '-d', type=float, help='follower offset')
parent_cam.add_argument('--fradius', '-q', type=float, help='follower radius')

parent_conj = ArgumentParser(add_help=False)
parent_conj.add_argument('--breadth', '-b', type=float, help='breadth, if 0 calculate optimal (default)')

parser_gen = subparsers.add_parser('gen', help='generate, unspecified variables set to default')
subparsers_gen = parser_gen.add_subparsers(dest='target')
subparsers_gen.required = True

parser_gen_travel = subparsers_gen.add_parser('travel', parents=[parent_travel],
                                              formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser_gen_travel.add_argument('--input', '-i', help='input file', required=True)
parser_gen_travel.set_defaults(kind='linear', order=3, n=1, steps=10000)

parser_gen_cam = subparsers_gen.add_parser('cam', parents=[parent_cam],
                                           formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser_gen_cam.set_defaults(radius=0, ccw=False, follower='roller', offset=0, fradius=0)

parser_gen_conj = subparsers_gen.add_parser('conj', parents=[parent_conj])
parser_gen_conj.set_defaults(breadth=0)

# Update has the same arguments as gen, but without overwriting with default values
parser_update = subparsers.add_parser('update', help='update, unspecified variables unmodified')
subparsers_update = parser_update.add_subparsers(dest='target')
subparsers_update.required = True
parser_update_travel = subparsers_update.add_parser('travel', parents=[parent_travel])
parser_update_cam = subparsers_update.add_parser('cam', parents=[parent_cam])
parser_update_conj = subparsers_update.add_parser('conj', parents=[parent_conj])

parser_load = subparsers.add_parser('load', help='load from file')
parser_load.add_argument('target', choices=['travel', 'cam'])
parser_load.add_argument('file', help='input file')

parser_save = subparsers.add_parser('save', help='save to file')
parser_save.add_argument('target', choices=targets)
parser_save.add_argument('file', help='output file')

parser_draw = subparsers.add_parser('draw', help='plot representation')
parser_draw.add_argument('targets', nargs='+', choices=targets)
parser_draw.add_argument('--unroll', '-u', action='store_true')
parser_draw.add_argument('--cartesian', '-c', action='store_true')

parser_print = subparsers.add_parser('print', help='show current variables')

parser_export = subparsers.add_parser('export', help='export')

parser_sim = subparsers.add_parser('sim', help='dynamic simulation')
parser_sim_velocity = parser_sim.add_mutually_exclusive_group(required=False)
parser_sim_velocity.add_argument('--omega', '-w', type=float, default=1, help='angular velocity')
parser_sim_velocity.add_argument('--rpm', '-r', type=float, help='revolutions per minute')
parser_sim.add_argument('--gravity', '-g', type=float, default=9.8, help='gravitational acceleration')
# TODO Simulation with conj, not simple

travel = Travel()
follower = Follower()
cam = Cam(travel, follower)

while True:
    try:
        command = input('camdesign: ')
        args = parser.parse_args(command.split())

        # HELP
        if args.command == 'help':
            parser.print_help()

        # EXIT
        elif args.command == 'exit':
            exit()

        # GEN
        elif args.command == 'gen':
            if args.target == 'travel':
                travel.gen(args.input, args.kind, args.order, args.steps, args.n)
                if cam() and not cam.loaded:
                    print('Updating cam')
                    cam.gen()
            elif args.target == 'cam':
                if not travel():
                    print('Travel undefined')
                    continue
                follower.update(args.follower, args.offset, args.fradius)
                cam.gen(args.radius, args.ccw)
            elif args.target == 'conj':
                if not cam():
                    print('Cam undefined')
                    continue
                cam.gen_conjugated(args.breadth)

        # LOAD
        elif args.command == 'load':
            if args.target == 'travel':
                travel.load(args.file)
            elif args.target == 'cam':
                fileio.write(args.file, travel.x, travel.y)

        # SAVE
        elif args.command == 'save':
            if args.target == 'travel':
                if not travel():
                    print('Travel undefined')
                    continue
                fileio.write(args.file, travel.x, travel.y)
            elif args.target == 'cam':
                if not cam():
                    print('Cam undefined')
                    continue
                fileio.write(args.file, cam.pcoords[0], cam.pcoords[1])

        # DRAW
        elif args.command == 'draw':
            if 'travel' in args.targets:
                if not travel():
                    print('Travel undefined')
                    continue
                ax = plt.subplot(111)
                ax.margins(0.1)
                ax.plot(travel.x, travel.y)
                plt.title('Follower travel')
                plt.show()
            if 'cam' in args.targets or 'conj' in args.targets:
                if not cam():
                    print('Cam undefined')
                    continue
                plotted = []
                if 'cam' in args.targets:
                    plotted.extend(cam.pcoords[:])
                if 'conj' in args.targets:
                    if not cam.conj():
                        # Maybe should call generation instead
                        print('Conjugated cam undefined')
                        continue
                    plotted.extend(cam.conj_pcoords[:])
                if args.unroll:
                    ax = plt.subplot()
                    ax.margins(0.1)
                    ax.plot(*plotted)
                else:
                    if args.cartesian:
                        ax = plt.subplot()
                        ax.axis('equal')
                        ax.margins(0.1)
                        ax.plot(*plot_polar(*plotted))
                    else:
                        # Not working well
                        # plotted[0] += np.pi/2*(1-np.sign(plotted[1]))
                        # plotted[1] = np.absolute(plotted[1])
                        # if len(plotted) > 2:
                        #     plotted[2] += np.pi/2*(1-np.sign(plotted[3]))
                        #     plotted[3] = np.absolute(plotted[3])
                        ax = plt.subplot(111, polar=True)
                        ax.set_theta_zero_location('N')
                        ax.plot(*plotted)
                        ax.margins(0.5)
                        ax.set_ylim(ymin=0)
                plt.show()

        # UPDATE
        elif args.command == 'update':
            if args.target == 'travel':
                if not travel.xpoints:
                    print('Loaded cam, unable to update')
                    continue
                print('Updating travel')
                travel.update(args.kind, args.order, args.steps, args.n)

                # If cam is generated (not loaded) repeat interpolation
                if cam() and not cam.loaded:
                    print('Updating cam')
                    cam.gen()
            elif args.target == 'cam':
                if not cam():
                    print('Cam not defined')
                    continue
                elif cam.loaded:
                    print('Loaded cam, unable to update')
                    continue
                follower.update(args.follower, args.offset, args.fradius)
                cam.gen(args.radius, args.ccw)
            elif args.target == 'conj':
                if not cam.conj():
                    print('Conjugated cam not defined')
                    continue
                cam.gen_conjugated(args.breadth)
        # SIMULATION
        elif args.command == 'sim':
            simulation.draw(cam, follower, args.omega if args.rpm is None else args.rpm*2*np.pi)
    except (ArgumentError, argparse.ArgumentError, argparse.ArgumentTypeError) as ex:
        if isinstance(ex.args[0], ArgumentParser):
            ex.args[0].print_usage()
            print(ex.args[1])
        else:
            print(ex)
    except FileNotFoundError:
        print('File not found')
    except HandledValueError as ex:
        print(ex)
