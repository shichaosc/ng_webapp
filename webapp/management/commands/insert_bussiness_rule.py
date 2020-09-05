from django.core.management.base import BaseCommand
from django.db import connection
import logging
from common.models import CommonBussinessRule, CommonRuleFormula
from course.models import CourseEdition
from classroom.models import ClassType
from tutor.models import UserLevel
from django.utils import timezone
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

FEE_BASE = {

    'Advanced': {
        # 'one2one': {
        #     UserLevel.FIRST_LEVEL: {
        #         CommonBussinessRule.BASE_PAY: {
        #             'min_amount': 0,
        #             'max_amount': 99999999,
        #             'amount': 0.4
        #         },
        #         CommonBussinessRule.INCENTIVE_PAY: {
        #             'lesson_sum_first': {
        #                 'min_amount': 6,
        #                 'max_amount': 20,
        #                 'amount': 0.1
        #             },
        #             'lesson_sum_second': {
        #                 'min_amount': 21,
        #                 'max_amount': 99999999,
        #                 'amount': 0.2
        #             }
        #         }
        #     },
        #     UserLevel.SECOND_LEVEL: {
        #         CommonBussinessRule.BASE_PAY: {
        #             'min_amount': 0,
        #             'max_amount': 99999999,
        #             'amount': 0.35
        #         },
        #         CommonBussinessRule.INCENTIVE_PAY: {
        #             'lesson_sum_first': {
        #                 'min_amount': 6,
        #                 'max_amount': 20,
        #                 'amount': 0.05
        #             },
        #             'lesson_sum_second': {
        #                 'min_amount': 21,
        #                 'max_amount': 99999999,
        #                 'amount': 0.1
        #             }
        #         }
        #     },
        #     UserLevel.THREE_LEVEL: {
        #         CommonBussinessRule.BASE_PAY: {
        #             'min_amount': 0,
        #             'max_amount': 99999999,
        #             'amount': 0.3
        #         },
        #         CommonBussinessRule.INCENTIVE_PAY: {
        #             'lesson_sum_first': {
        #                 'min_amount': 6,
        #                 'max_amount': 20,
        #                 'amount': 0.05
        #             },
        #             'lesson_sum_second': {
        #                 'min_amount': 21,
        #                 'max_amount': 99999999,
        #                 'amount': 0.1
        #             }
        #         }
        #     }
        # },
        'smallclass': {
            UserLevel.FIRST_LEVEL: {
                CommonBussinessRule.BASE_PAY: {
                    'min_amount': 0,
                    'max_amount': 99999999,
                    'amount': 0.4
                },
                CommonBussinessRule.INCENTIVE_PAY: {
                    'lesson_sum_first': {
                        'min_amount': 6,
                        'max_amount': 20,
                        'amount': 0.1
                    },
                    'lesson_sum_second': {
                        'min_amount': 21,
                        'max_amount': 99999999,
                        'amount': 0.2
                    }
                }
            },
            UserLevel.SECOND_LEVEL: {
                CommonBussinessRule.BASE_PAY: {
                    'min_amount': 0,
                    'max_amount': 99999999,
                    'amount': 0.35
                },
                CommonBussinessRule.INCENTIVE_PAY: {
                    'lesson_sum_first': {
                        'min_amount': 6,
                        'max_amount': 20,
                        'amount': 0.05
                    },
                    'lesson_sum_second': {
                        'min_amount': 21,
                        'max_amount': 99999999,
                        'amount': 0.1
                    }
                }
            },
            UserLevel.THREE_LEVEL: {
                CommonBussinessRule.BASE_PAY: {
                    'min_amount': 0,
                    'max_amount': 99999999,
                    'amount': 0.3
                },
                CommonBussinessRule.INCENTIVE_PAY: {
                    'lesson_sum_first': {
                        'min_amount': 6,
                        'max_amount': 20,
                        'amount': 0.05
                    },
                    'lesson_sum_second': {
                        'min_amount': 21,
                        'max_amount': 99999999,
                        'amount': 0.1
                    }
                }
            }
        }
    },
    'International Lite': {
        # 'one2one': {
        #     UserLevel.FIRST_LEVEL: {
        #         CommonBussinessRule.BASE_PAY: {
        #             'min_amount': 0,
        #             'max_amount': 99999999,
        #             'amount': 0.3
        #         },
        #         CommonBussinessRule.INCENTIVE_PAY: {
        #             'lesson_sum_first': {
        #                 'min_amount': 6,
        #                 'max_amount': 20,
        #                 'amount': 0.05
        #             },
        #             'lesson_sum_second': {
        #                 'min_amount': 21,
        #                 'max_amount': 99999999,
        #                 'amount': 0.1
        #             }
        #         }
        #     },
        #     UserLevel.SECOND_LEVEL: {
        #         CommonBussinessRule.BASE_PAY: {
        #             'min_amount': 0,
        #             'max_amount': 99999999,
        #             'amount': 0.3
        #         },
        #         CommonBussinessRule.INCENTIVE_PAY: {
        #             'lesson_sum_first': {
        #                 'min_amount': 6,
        #                 'max_amount': 20,
        #                 'amount': 0.05
        #             },
        #             'lesson_sum_second': {
        #                 'min_amount': 21,
        #                 'max_amount': 99999999,
        #                 'amount': 0.1
        #             }
        #         }
        #     },
        #     UserLevel.THREE_LEVEL: {
        #         CommonBussinessRule.BASE_PAY: {
        #             'min_amount': 0,
        #             'max_amount': 99999999,
        #             'amount': 0.3
        #         },
        #         CommonBussinessRule.INCENTIVE_PAY: {
        #             'lesson_sum_first': {
        #                 'min_amount': 6,
        #                 'max_amount': 20,
        #                 'amount': 0.05
        #             },
        #             'lesson_sum_second': {
        #                 'min_amount': 21,
        #                 'max_amount': 99999999,
        #                 'amount': 0.1
        #             }
        #         }
        #     }
        # },
        'smallclass': {
            UserLevel.FIRST_LEVEL: {
                CommonBussinessRule.BASE_PAY: {
                    'min_amount': 0,
                    'max_amount': 99999999,
                    'amount': 0.3
                },
                CommonBussinessRule.INCENTIVE_PAY: {
                    'lesson_sum_first': {
                        'min_amount': 6,
                        'max_amount': 20,
                        'amount': 0.05
                    },
                    'lesson_sum_second': {
                        'min_amount': 21,
                        'max_amount': 99999999,
                        'amount': 0.1
                    }
                }
            },
            UserLevel.SECOND_LEVEL: {
                CommonBussinessRule.BASE_PAY: {
                    'min_amount': 0,
                    'max_amount': 99999999,
                    'amount': 0.3
                },
                CommonBussinessRule.INCENTIVE_PAY: {
                    'lesson_sum_first': {
                        'min_amount': 6,
                        'max_amount': 20,
                        'amount': 0.05
                    },
                    'lesson_sum_second': {
                        'min_amount': 21,
                        'max_amount': 99999999,
                        'amount': 0.1
                    }
                }
            },
            UserLevel.THREE_LEVEL: {
                CommonBussinessRule.BASE_PAY: {
                    'min_amount': 0,
                    'max_amount': 99999999,
                    'amount': 0.3
                },
                CommonBussinessRule.INCENTIVE_PAY: {
                    'lesson_sum_first': {
                        'min_amount': 6,
                        'max_amount': 20,
                        'amount': 0.05
                    },
                    'lesson_sum_second': {
                        'min_amount': 21,
                        'max_amount': 99999999,
                        'amount': 0.1
                    }
                }
            }
        }
    },
    'SG Program': {
        # 'one2one': {
        #     UserLevel.FIRST_LEVEL: {
        #         CommonBussinessRule.BASE_PAY: {
        #             'min_amount': 0,
        #             'max_amount': 99999999,
        #             'amount': 0.4
        #         },
        #         CommonBussinessRule.INCENTIVE_PAY: {
        #             'lesson_sum_first': {
        #                 'min_amount': 6,
        #                 'max_amount': 20,
        #                 'amount': 0.1
        #             },
        #             'lesson_sum_second': {
        #                 'min_amount': 21,
        #                 'max_amount': 99999999,
        #                 'amount': 0.2
        #             }
        #         }
        #     },
        #     UserLevel.SECOND_LEVEL: {
        #         CommonBussinessRule.BASE_PAY: {
        #             'min_amount': 0,
        #             'max_amount': 99999999,
        #             'amount': 0.35
        #         },
        #         CommonBussinessRule.INCENTIVE_PAY: {
        #             'lesson_sum_first': {
        #                 'min_amount': 6,
        #                 'max_amount': 20,
        #                 'amount': 0.05
        #             },
        #             'lesson_sum_second': {
        #                 'min_amount': 21,
        #                 'max_amount': 99999999,
        #                 'amount': 0.1
        #             }
        #         }
        #     },
        #     UserLevel.THREE_LEVEL: {
        #         CommonBussinessRule.BASE_PAY: {
        #             'min_amount': 0,
        #             'max_amount': 99999999,
        #             'amount': 0.3
        #         },
        #         CommonBussinessRule.INCENTIVE_PAY: {
        #             'lesson_sum_first': {
        #                 'min_amount': 6,
        #                 'max_amount': 20,
        #                 'amount': 0.05
        #             },
        #             'lesson_sum_second': {
        #                 'min_amount': 21,
        #                 'max_amount': 99999999,
        #                 'amount': 0.1
        #             }
        #         }
        #     }
        # },
        'smallclass': {
            UserLevel.FIRST_LEVEL: {
                CommonBussinessRule.BASE_PAY: {
                    'min_amount': 0,
                    'max_amount': 99999999,
                    'amount': 0.4
                },
                CommonBussinessRule.INCENTIVE_PAY: {
                    'lesson_sum_first': {
                        'min_amount': 6,
                        'max_amount': 20,
                        'amount': 0.1
                    },
                    'lesson_sum_second': {
                        'min_amount': 21,
                        'max_amount': 99999999,
                        'amount': 0.2
                    }
                }
            },
            UserLevel.SECOND_LEVEL: {
                CommonBussinessRule.BASE_PAY: {
                    'min_amount': 0,
                    'max_amount': 99999999,
                    'amount': 0.35
                },
                CommonBussinessRule.INCENTIVE_PAY: {
                    'lesson_sum_first': {
                        'min_amount': 6,
                        'max_amount': 20,
                        'amount': 0.05
                    },
                    'lesson_sum_second': {
                        'min_amount': 21,
                        'max_amount': 99999999,
                        'amount': 0.1
                    }
                }
            },
            UserLevel.THREE_LEVEL: {
                CommonBussinessRule.BASE_PAY: {
                    'min_amount': 0,
                    'max_amount': 99999999,
                    'amount': 0.3
                },
                CommonBussinessRule.INCENTIVE_PAY: {
                    'lesson_sum_first': {
                        'min_amount': 6,
                        'max_amount': 20,
                        'amount': 0.05
                    },
                    'lesson_sum_second': {
                        'min_amount': 21,
                        'max_amount': 99999999,
                        'amount': 0.1
                    }
                }
            }
        }
    }
}

# 老师累计对同一个learning_group上课超过规定课时进行额外奖励
FIRST_LESSON_SUM = 6
SECOND_LESSON_SUM = 20




class Command(BaseCommand):

    help = '插入不同等级老师工资规则'


    def handle(self, *args, **options):
        now = timezone.now()
        start_time = now - timedelta(3)
        fifty_years = now + timedelta(days=50*365)

        for programme_name in FEE_BASE.keys():
            course_edition = CourseEdition.objects.filter(edition_name=programme_name).first()
            class_type_dict = FEE_BASE[programme_name]
            for class_type_name in class_type_dict.keys():
                tutor_grade_dict = class_type_dict[class_type_name]
                class_type = ClassType.objects.filter(name=class_type_name).first()

                for tutor_grade_level in tutor_grade_dict.keys():
                    user_level = UserLevel.objects.filter(grade=tutor_grade_level).first()

                    pay_type_dict = tutor_grade_dict[tutor_grade_level]

                    for pay_type in pay_type_dict.keys():
                        CommonBussinessRule.objects.filter(rule_type=pay_type,
                                                           course_edition=course_edition,
                                                           class_type=class_type,
                                                           user_level=user_level,
                                                           local_area=CommonBussinessRule.SINGAPORE).delete()
                        if pay_type == CommonBussinessRule.INCENTIVE_PAY:
                            rule_type_dict = pay_type_dict[pay_type]
                            for key, value in rule_type_dict.items():
                                business_rule = CommonBussinessRule()
                                business_rule.course_edition = course_edition
                                business_rule.class_type = class_type
                                business_rule.user_level = user_level
                                business_rule.local_area = CommonBussinessRule.OTHER_AREA
                                business_rule.valid_start = start_time
                                business_rule.valid_end = fifty_years
                                business_rule.rule_type = CommonBussinessRule.INCENTIVE_PAY
                                business_rule.desc = '{}-{}'.format(value['min_amount'], value['max_amount'])
                                business_rule.save()

                                rule_formula = CommonRuleFormula()
                                rule_formula.rule = business_rule
                                rule_formula.min_amount = value['min_amount']
                                rule_formula.max_amount = value['max_amount']
                                rule_formula.amount = value['amount']
                                rule_formula.save()
                        elif pay_type == CommonBussinessRule.BASE_PAY:

                            business_rule = CommonBussinessRule()
                            business_rule.course_edition = course_edition
                            business_rule.class_type = class_type
                            business_rule.user_level = user_level
                            business_rule.local_area = CommonBussinessRule.OTHER_AREA
                            business_rule.valid_start = start_time
                            business_rule.valid_end = fifty_years
                            business_rule.rule_type = CommonBussinessRule.BASE_PAY
                            business_rule.desc = 'BASE'
                            business_rule.save()

                            rule_type_dict = pay_type_dict[pay_type]
                            rule_formula = CommonRuleFormula()
                            rule_formula.rule = business_rule
                            rule_formula.min_amount = rule_type_dict['min_amount']
                            rule_formula.max_amount = rule_type_dict['max_amount']
                            rule_formula.amount = rule_type_dict['amount']
                            rule_formula.save()

