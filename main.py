import argparse
from travel import Travel
from cam import Cam
from follower import Follower
import matplotlib.pyplot as plt
import fileio


# Overriding ArgumentParser error handling
class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise Exception(self, message)

    # Do not exit after printing help
    def exit(self, status=0, message=None):
        if message:
            self._print_message(message)
        self.error(None)

interp = ['spline', 'linear', 'harmonic', 'cycloidal', 'parabolic', 'polynomial']

parser = ArgumentParser(description='camdesign', prog='', add_help=False)
subparsers = parser.add_subparsers(dest='command')
subparsers.required = True

parser_help = subparsers.add_parser('help', help='show this help message')
parser_exit = subparsers.add_parser('exit')

parser_gen = subparsers.add_parser('gen', help='generate, unspecified variables set to default')
subparsers_gen = parser_gen.add_subparsers(dest='target')
subparsers_gen.required = True

parser_gen_travel = subparsers_gen.add_parser('travel')
parser_gen_travel.add_argument('--input', '-i', help='input file', required=True)
parser_gen_travel.add_argument('--kind', '-k', choices=interp, default='linear',
                               help='kind of interpolation')
parser_gen_travel.add_argument('--order', '-o', type=int, default=3, help='spline/polynomial order')
parser_gen_travel.add_argument('-n', type=int, default=1)
parser_gen_travel.add_argument('--steps', '-s', type=int, default=10000)

parser_gen_cam = subparsers_gen.add_parser('cam')
parser_gen_cam.add_argument('--radius', '-r', type=float, default=0, help='base radius')
parser_gen_cam.add_argument('--ccw', action='store_true')
parser_gen_cam.add_argument('--follower', '-f', choices=['knife', 'roller', 'flat'], default='knife',
                            help='follower type')
parser_gen_cam.add_argument('--offset', '-d', type=float, default=0, help='follower offset')
parser_gen_cam.add_argument('--fradius', '-q', type=float, help='follower radius')

# Same arguments as gen, but without defaults
parser_update = subparsers.add_parser('update', help='update, unspecified variables unmodified')
subparsers_update = parser_update.add_subparsers(dest='target')
subparsers_update.required = True

parser_update_travel = subparsers_update.add_parser('travel')
parser_update_travel.add_argument('--kind', '-k', choices=interp,
                                  help='kind of interpolation')
parser_update_travel.add_argument('--order', '-o', type=int, help='spline/polynomial order')
parser_update_travel.add_argument('-n', type=int)
parser_update_travel.add_argument('--steps', '-s', type=int)

parser_update_cam = subparsers_update.add_parser('cam')
parser_update_cam.add_argument('--radius', '-r', type=float, help='base radius')
parser_update_cam.add_argument('--ccw', action='store_const', const=True)
parser_update_cam.add_argument('--follower', '-f', choices=['knife', 'roller', 'flat'], help='follower type')
parser_update_cam.add_argument('--offset', '-d', type=float, help='follower offset')
parser_update_cam.add_argument('--fradius', '-q', type=float, help='follower radius')

parser_load = subparsers.add_parser('load', help='load from file')
parser_load.add_argument('target', choices=['travel', 'cam'])
parser_load.add_argument('file', help='input file')

parser_save = subparsers.add_parser('save', help='save to file')
parser_save.add_argument('target', choices=['travel', 'cam'])
parser_save.add_argument('file', help='output file')

parser_draw = subparsers.add_parser('draw', help='plot representation')
parser_draw.add_argument('target', choices=['travel', 'cam'])

parser_print = subparsers.add_parser('print', help='show current variables')

parser_export = subparsers.add_parser('export', help='export')

# parser_gen.add_argument('--precision', '-p', type=float, default=0.001)

parser_simulate = subparsers.add_parser('sim', help='dynamic simulation')

travel = Travel()
follower = Follower()
cam = Cam(travel, follower)

while True:
    command = input('camdesign: ')
    try:
        args = parser.parse_args(command.split())
    except (Exception, argparse.ArgumentError, argparse.ArgumentTypeError) as ex:
        if ex.args[1] is not None:
            ex.args[0].print_usage()
            print(ex.args[1])
        continue

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
            follower.update(args.follower, args.offset, args.radius)
            cam.gen(args.radius, args.ccw)

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
            fileio.write(args.file, cam.theta, cam.rho)

    # DRAW
    elif args.command == 'draw':
        if args.target == 'travel':
            if not travel():
                print('Travel undefined')
                continue
            ax = plt.subplot(111)
            ax.margins(0.1)
            ax.plot(travel.x, travel.y)
            plt.title('Follower travel')
            plt.show()
        elif args.target == 'cam':
            if not cam():
                print('Cam undefined')
                continue
            ax = plt.subplot(111, polar=True)
            ax.set_theta_zero_location('N')
            ax.plot(cam.theta, cam.rho)
            ax.margins(1)
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
