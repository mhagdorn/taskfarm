from taskfarm import db
from taskfarm.models import User
import argparse
import sys


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--user', help="the taskfarm user")
    parser.add_argument('-p', '--password',
                        help="the password of the taskfarm user")
    parser.add_argument('--init-db', action='store_true',
                        default=False, help="initialise database")

    args = parser.parse_args()

    if args.init_db:
        db.create_all()

    if args.user is not None:
        if args.password is None:
            parser.error('need to set password')
            sys.exit(1)
        u = User(username=args.user)
        u.hash_password(args.password)
        db.session.add(u)
        db.session.commit()


if __name__ == '__main__':
    main()
