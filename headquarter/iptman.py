import iptc
import logging

logging.basicConfig(format='[%(levelname)s]\t%(asctime)s\t%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                    level=logging.DEBUG)
log = logging.getLogger("iptman")

class IptMan():
    def __init__(self):
        pass

    @staticmethod
    def insert_rule(port):
        try:
            # New Rule.
            rule = iptc.Rule()
            rule.protocol = "tcp"

            # Add match to the rule.
            match = iptc.Match(rule, "tcp")
            match.sport = str(port)
            rule.add_match(match)

            # Add target to the rule.
            target = iptc.Target(rule, "ACCEPT")
            rule.target = target

            # Insert rule to the OUTPUT chain in filter Table.
            output_chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), "OUTPUT")
            output_chain.insert_rule(rule)

        except Exception, e:
            raise e

    @staticmethod
    def delete_rule(port):
        try:
            filter_table = iptc.Table(iptc.Table.FILTER)
            output_chain = iptc.Chain(filter_table, "OUTPUT")
            rule_del = None
            for rule in output_chain.rules:
                sport = str(rule.matches[0].parameters["sport"])
                if sport == str(port):
                    rule_del = rule
                    break

            if rule_del is not None:
                output_chain.delete_rule(rule_del)

        except Exception, e:
            raise e

    @staticmethod
    def get_rule_counter(port):
        try:
            filter_table = iptc.Table(iptc.Table.FILTER)
            filter_table.refresh()

            output_chain = iptc.Chain(filter_table, "OUTPUT")

            bytes_counts = None

            for rule in output_chain.rules:
                sport = str(rule.matches[0].parameters["sport"])
                # log.debug(rule.get_counters())
                if sport == str(port):
                    counter = rule.get_counters()
                    packets = counter[0]
                    bytes_counts = counter[1]
                    log.debug("packet #:" + str(packets))
                    log.debug("bytes #:" + str(bytes_counts))
                    break
            if bytes_counts is None:
                raise Exception("NotFoundPort")

            return bytes_counts

        except Exception, e:
            raise e


def unit_test():
    pass

if __name__ == "__main__":
    unit_test()