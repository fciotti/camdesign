parser.add_argument('--steps', '-s', type=int, default=10000, help='global precision')

parser_gen = subparsers.add_parser('gen')
#parser_gen.add_argument('cam', choices=['rot', 'transl', 'travel'], default='rot', help='what is generated')
parser_gen.add_argument('--type', '-t', choices=['spline', 'linear'], default='linear',
                        help='type of interpolation')
parser_gen.add_argument('--order', '-k', type=int, default=3, help='spline order')
parser_gen.add_argument('--input', '-i', help='input file', required=True)
parser_gen.add_argument('-n', type=int, default=1)
parser_gen.add_argument('--radius', '-r', type=float, help='base radius', required=True)
parser_gen.add_argument('--follower', '-f', choices=['knife', 'roller', 'flat'], default='knife',
                        help='follower type')
parser_gen.add_argument('--offset', '-d', type=float, default=0)
parser_gen.add_argument('--fradius', '-q', type=float, help='follower radius')
parser_gen.add_argument('--output', '-o', help='output file')
parser_gen.add_argument('--ccw', action='store_true')