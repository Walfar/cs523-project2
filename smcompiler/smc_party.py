"""
Implementation of an SMC client.

MODIFY THIS FILE.
"""
# You might want to import more classes if needed.

import json
from typing import Dict
import jsonpickle

from sympy import Mul

from communication import Communication
from expression import (
    Addition,
    Expression,
    Multiplication,
    Secret,
    Scalar,
    Substraction
)
from protocol import ProtocolSpec
from secret_sharing import(
    reconstruct_secret,
    share_secret,
    Share,
)

# Feel free to add as many imports as you want.


class SMCParty:
    """
    A client that executes an SMC protocol to collectively compute a value of an expression together
    with other clients.

    Attributes:
        client_id: Identifier of this client
        server_host: hostname of the server
        server_port: port of the server
        protocol_spec (ProtocolSpec): Protocol specification
        value_dict (dict): Dictionary assigning values to secrets belonging to this client.
    """

    def __init__(
            self,
            client_id: str,
            server_host: str,
            server_port: int,
            protocol_spec: ProtocolSpec,
            value_dict: Dict[Secret, int]
        ):
        self.comm = Communication(server_host, server_port, client_id)

        self.client_id = client_id
        self.protocol_spec = protocol_spec
        self.value_dict = value_dict

        # This dict contains the corresponding part of the client for each secret when sharing it
        self.myShares = {}

    def run(self) -> int:
        """
        The method the client use to do the SMC.
        """

        # Firstly, the client shares all his secrets with the other parties, using their id as the channel
        for secret, value in self.value_dict.items():
            shares = share_secret(value, len(self.protocol_spec.participant_ids))
            for i in range(len(self.protocol_spec.participant_ids)):
                # We iterate over all participants, and send shares. When the id is ourselves, we store the share.
                if self.protocol_spec.participant_ids[i] == self.client_id:
                    self.myShares[secret.id] = shares[i]
                else:   
                    self.comm.send_private_message(self.protocol_spec.participant_ids[i], secret.id, jsonpickle.encode(shares[i]))
        
        # Then, we compute the protocol expression for the first round
        myShare = self.process_expression(self.protocol_spec.expr) 

        # Final round, we publish the obtained value and compute the result with the other published values
        self.comm.publish_message("final", jsonpickle.encode(myShare))
        share_list = list()
        for participant_id in self.protocol_spec.participant_ids:
            if participant_id  == self.client_id:
                share_list.append(myShare)
            else:    
                share_list.append(jsonpickle.decode(self.comm.retrieve_public_message(participant_id, "final")))           
        return reconstruct_secret(share_list)        


    # Suggestion: To process expressions, make use of the *visitor pattern* like so:
    def process_expression(
            self,
            expr: Expression
        ) -> Share:
        if isinstance(expr, Addition):
            # If scalar in the addition
            if isinstance(expr.expr1, Scalar) and isinstance(expr.expr2, Expression):
                if self.client_id == self.protocol_spec.participant_ids[0]:
                    return Share(expr.expr1.value) + self.process_expression(expr.expr2)
                else:
                    return self.process_expression(expr.expr2)
            if isinstance(expr.expr1, Expression) and isinstance(expr.expr2, Scalar):
                if self.client_id == self.protocol_spec.participant_ids[0]:
                    return self.process_expression(expr.expr1) + Share(expr.expr2.value)
                else:
                    return self.process_expression(expr.expr1) 

            # If no scalar in the addition
            left = self.process_expression(expr.expr1)
            right = self.process_expression(expr.expr2)
            return left + right           

        if isinstance(expr, Secret):
            if expr in (list(self.value_dict.keys())):
                return self.myShares[expr.id]
            else:
                return jsonpickle.decode(self.comm.retrieve_private_message(expr.id))    

        if isinstance(expr, Scalar):
            return Share(expr.value)

        if isinstance(expr, Substraction):
            if isinstance(expr.expr1, Scalar) and isinstance(expr.expr2, Expression):
                if self.client_id == self.protocol_spec.participant_ids[0]:
                    return Share(expr.expr1.value) - self.process_expression(expr.expr2)
                else:
                    return Share(0) - self.process_expression(expr.expr2)
            if isinstance(expr.expr1, Expression) and isinstance(expr.expr2, Scalar):
                if self.client_id == self.protocol_spec.participant_ids[0]:
                    return self.process_expression(expr.expr1) - Share(expr.expr2.value)
                else:
                    return self.process_expression(expr.expr1) 

            # If no scalar in the addition
            left = self.process_expression(expr.expr1)
            right = self.process_expression(expr.expr2)
            print(f"left for {self.client_id} is {left.bn}")
            print(f"right for {self.client_id} is {right.bn}")
            return left - right      

        if isinstance(expr, Multiplication):
            left = self.process_expression(expr.expr1)
            right = self.process_expression(expr.expr2)
            print("mul")
            if isinstance(expr.expr1, Secret) and isinstance(expr.expr2, Secret):
                print("instance")
                a, b, c = self.comm.retrieve_beaver_triplet_shares(self.protocol_spec.expr.id)
                print(f"a is {a}, b is {b}, c is {c}")
                share_x = left - Share(a)
                share_y = right - Share(b)
                self.comm.publish_message("share_x", jsonpickle.encode(share_x))
                self.comm.publish_message("share_y", jsonpickle.encode(share_y))

                share_x_list = list()
                share_y_list = list()
                for participant_id in self.protocol_spec.participant_ids:
                    if participant_id  == self.client_id:
                        share_x_list.append(share_x)
                        share_y_list.append(share_y)
                    else:    
                        share_x_list.append(jsonpickle.decode(self.comm.retrieve_public_message(participant_id, "share_x")))
                        share_y_list.append(jsonpickle.decode(self.comm.retrieve_public_message(participant_id, "share_y")))
                share_x_val = Share(reconstruct_secret(share_x_list))
                share_y_val = Share(reconstruct_secret(share_y_list))
                share_z = Share(c) + left * share_y_val + right * share_x_val
                if self.client_id == self.protocol_spec.participant_ids[0]:
                    return share_z - share_x_val * share_y_val
                return share_z    

            else:
                print("else")
                return left * right    
        # Call specialized methods for each expression type, and have these specialized
        # methods in turn call `process_expression` on their sub-expressions to process
        # further.
        pass

    # Feel free to add as many methods as you want.