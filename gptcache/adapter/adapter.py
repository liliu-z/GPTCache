import logging

from ..core import cache, time_cal
from ..util.error import NotInitError


def adapt(llm_handler, cache_data_convert, update_cache_callback, *args, **kwargs):
    chat_cache = kwargs.pop("cache_obj", cache)
    if not chat_cache.has_init:
        raise NotInitError()
    cache_enable = chat_cache.cache_enable_func(*args, **kwargs)
    context = kwargs.get("cache_context", {})
    embedding_data = None
    # you want to retry to send the request to chatgpt when the cache is negative
    cache_skip = kwargs.get("cache_skip", False)
    pre_embedding_data = chat_cache.pre_embedding_func(kwargs,
                                                       extra_param=context.get("pre_embedding_func", None))
    if cache_enable and not cache_skip:
        embedding_data = time_cal(chat_cache.embedding_func,
                                  func_name="embedding",
                                  report_func=chat_cache.report.embedding,
                                  )(pre_embedding_data, extra_param=context.get("embedding_func", None))
        cache_data_list = time_cal(chat_cache.data_manager.search,
                                   func_name="search",
                                   report_func=chat_cache.report.search,
                                   )(embedding_data, extra_param=context.get('search', None))
        if cache_data_list is None:
            cache_data_list = []
        cache_answers = []
        for cache_data in cache_data_list:
            cache_question, cache_answer = chat_cache.data_manager.get_scalar_data(
                cache_data, extra_param=context.get('get_scalar_data', None))
            rank = chat_cache.evaluation_func({
                "question": pre_embedding_data,
                "embedding": embedding_data,
            }, {
                "question": cache_question,
                "answer": cache_answer,
                "search_result": cache_data,
            }, extra_param=context.get('evaluation', None))
            if (chat_cache.similarity_positive and rank >= chat_cache.similarity_threshold) \
                    or (not chat_cache.similarity_positive and rank <= chat_cache.similarity_threshold):
                cache_answers.append((rank, cache_answer))
        cache_answers = sorted(cache_answers, key=lambda x: x[0], reverse=True)
        if len(cache_answers) != 0:
            return_message = chat_cache.post_process_messages_func([t[1] for t in cache_answers])
            chat_cache.report.hint_cache()
            return cache_data_convert(return_message)

    next_cache = chat_cache.next_cache
    if next_cache:
        kwargs["cache_obj"] = next_cache
        llm_data = adapt(llm_handler, cache_data_convert, update_cache_callback, *args, **kwargs)
    else:
        llm_data = llm_handler(*args, **kwargs)

    if cache_enable:
        try:
            def update_cache_func(handled_llm_data):
                chat_cache.data_manager.save(pre_embedding_data,
                                             handled_llm_data,
                                             embedding_data,
                                             extra_param=context.get('save', None))

            llm_data = update_cache_callback(llm_data, update_cache_func)
        except Exception as e:
            logging.warning(f"failed to save the data to cache, error:{e}")
    return llm_data